import json
import re
import httpx
from app.models.ai_model import AIModel
from app.config import settings
from cryptography.fernet import Fernet
import hashlib
import base64
import logging

logger = logging.getLogger(__name__)

def get_cipher():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_api_key(raw_key: str) -> str:
    f = get_cipher()
    return f.encrypt(raw_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    f = get_cipher()
    return f.decrypt(encrypted_key.encode()).decode()

DEFAULT_SYSTEM_PROMPT = """你是一位顶尖的加密货币量化高频交易专家，专精于BTC/USDT 5分钟级（M5）K线的超短线多空走势研判。
你的核心任务是深入剖析提供的5分钟级实时行情、近期K线形态与量化指标（MACD/RSI/布林带/EMA/SMA），给出极具量化说服力、逻辑严密的下一个5分钟K线涨跌（UP/DOWN）预测；若多空信号严重冲突则果断观望（SKIP）。

【深度量化分析要求】：
1. 动能结构：重点研判 RSI(14) 强弱位置（超买/超卖/中轴50分水岭）及 MACD 柱能扩张或收敛，DIF与DEA是否形成动能背离或交叉。
2. 均线势能：EMA(7)与EMA(25)快慢线多空发散态势，当前价相对长线基准 SMA(99) 的压制或支撑力度。
3. 通道与价格行为：布林带(20,2)收口蓄势还是张口扩张，K线影线形态（Pinbar、多空吞没、放量实体突破）。

【输出格式严苛规定】：
必须且仅输出合法的纯 JSON 格式对象，严禁包含任何 Markdown 标记（如```json）或外部注释：
{
  "prediction": "UP" 或 "DOWN" 或 "SKIP",
  "confidence": 0.50 到 0.95 之间的浮点数,
  "reasoning": "中文决策理由，字数在70-160字之间。必须以专业量化交易员口吻，直接引用指标数值（如RSI处于xx、EMA7穿过EMA25、回踩布林中轨xx），层层推导，逻辑连贯且有极强说服力。"
}

【决策原则】：
- 看涨 (UP)：必须指出多头动量引爆点、均线或布林通道的支撑有效性。
- 看跌 (DOWN)：必须指出顶背离、均线死叉压制或破位风险。
- 观望 (SKIP)：仅在多空指标严重矛盾且无确定性盈亏比时使用，并说明风险点。"""

class AIPredictorService:
    async def predict(self, ai_model: AIModel, market_data: dict, indicators: dict) -> dict:
        try:
            api_key = decrypt_api_key(ai_model.api_key_encrypted)
            
            # Build rich market context
            prompt_parts = [
                "【BTC/USDT 5分钟(M5)周期量化决策输入】",
                f"当前最新现价: ${market_data.get('price', 'N/A')}",
                f"24小时涨跌幅: {market_data.get('price_change_pct', 'N/A')}%",
                f"24小时成交量: {market_data.get('volume_24h', 'N/A')} USDT",
                f"24小时高/低点: ${market_data.get('high_24h', 'N/A')} / ${market_data.get('low_24h', 'N/A')}",
                "",
                "【最近连续5根5分钟K线流水（由旧到新）】",
            ]
            
            recent_klines = market_data.get("recent_klines", [])
            for i, k in enumerate(recent_klines[-5:]):
                direction = "▲红阳" if k.get("close_price", 0) >= k.get("open_price", 0) else "▼绿阴"
                prompt_parts.append(
                    f"  M5[{i+1}] {direction} 开:{k.get('open_price',0):.2f} 高:{k.get('high_price',0):.2f} "
                    f"低:{k.get('low_price',0):.2f} 收:{k.get('close_price',0):.2f} 量:{k.get('volume',0):.1f}"
                )
            
            prompt_parts.extend([
                "",
                "【核心技术指标当前读数】",
                f"MACD (12, 26, 9): DIF={indicators.get('macd', 'N/A')}, DEA={indicators.get('macd_signal', 'N/A')}, HIST={indicators.get('macd_hist', 'N/A')}",
                f"RSI(14): {indicators.get('rsi_14', 'N/A')}",
                f"布林带 (20, 2): 上轨={indicators.get('bb_upper', 'N/A')}, 中轨={indicators.get('bb_middle', 'N/A')}, 下轨={indicators.get('bb_lower', 'N/A')}",
                f"指数均线: EMA(7)={indicators.get('ema_7', 'N/A')}, EMA(25)={indicators.get('ema_25', 'N/A')}",
                f"基准均线: SMA(99)={indicators.get('sma_99', 'N/A')}",
                "",
                "请基于上述5分钟指标与K线量价，推演未来5分钟K线收盘涨跌。严格按JSON输出。"
            ])
            
            prompt = "\n".join(prompt_parts)
            system_prompt = ai_model.system_prompt or DEFAULT_SYSTEM_PROMPT
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": ai_model.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": ai_model.temperature,
                "max_tokens": 500,
            }
            
            base_url = ai_model.base_url.strip().rstrip("/")
            endpoint = base_url if "/chat/completions" in base_url else f"{base_url}/chat/completions"
            
            client_kwargs = {"timeout": 60.0}
            if settings.HTTP_PROXY:
                client_kwargs["proxy"] = settings.HTTP_PROXY
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"]
                return self._parse_response(content)
                
        except httpx.TimeoutException:
            logger.warning(f"AI model {ai_model.name} timed out")
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": "AI模型请求超时，网络或API无响应"}
        except httpx.HTTPStatusError as e:
            err_detail = ""
            try:
                err_json = e.response.json()
                if isinstance(err_json, dict):
                    if "error" in err_json:
                        err_obj = err_json["error"]
                        if isinstance(err_obj, dict) and "message" in err_obj:
                            err_detail = f": {err_obj['message']}"
                        elif isinstance(err_obj, str):
                            err_detail = f": {err_obj}"
                    elif "message" in err_json:
                        err_detail = f": {err_json['message']}"
            except Exception:
                if e.response.text:
                    err_detail = f": {e.response.text[:120]}"
            msg = f"AI模型接口返回错误码 HTTP {e.response.status_code}{err_detail}"
            logger.error(f"AI model {ai_model.name} HTTP error: {msg}")
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": msg}
        except Exception as e:
            logger.error(f"AI model {ai_model.name} error: {e}")
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": f"调用AI接口失败: {str(e)}"}
    
    def _parse_response(self, content: str) -> dict:
        content = content.strip()
        
        # Strategy 1: Direct JSON parse
        try:
            data = json.loads(content)
            return self._validate_data(data)
        except json.JSONDecodeError:
            pass
            
        # Strategy 2: Extract from markdown code blocks ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return self._validate_data(data)
            except json.JSONDecodeError:
                pass
                
        # Strategy 3: Find any {...} substring containing "prediction"
        match = re.search(r"\{[^{}]*\"prediction\"[^{}]*\}", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return self._validate_data(data)
            except json.JSONDecodeError:
                pass
                
        logger.warning(f"Failed to parse JSON from AI response: {content[:200]}")
        return {
            "prediction": "SKIP",
            "confidence": 0.0,
            "reasoning": f"模型返回格式解析失败: {content[:100]}"
        }

    def _validate_data(self, data: dict) -> dict:
        pred = str(data.get("prediction", "SKIP")).upper().strip()
        if pred not in ["UP", "DOWN", "SKIP"]:
            pred = "SKIP"
            
        try:
            conf = float(data.get("confidence", 0.5))
            conf = max(0.0, min(1.0, conf))
        except (ValueError, TypeError):
            conf = 0.5
            
        reasoning = str(data.get("reasoning", "")).strip()
        
        return {
            "prediction": pred,
            "confidence": conf,
            "reasoning": reasoning
        }

ai_predictor_service = AIPredictorService()
