import httpx
import json
import logging
from app.models.ai_model import AIModel
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib

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

DEFAULT_SYSTEM_PROMPT = """You are an expert cryptocurrency quantitative analyst specializing in BTC/USDT short-term price prediction. 
Your task is to analyze 5-minute interval market data and predict whether the price will go UP or DOWN in the next 5-minute candle.

Analysis methodology:
1. Trend Analysis: EMA crossovers (EMA7 vs EMA25), price position relative to SMA99
2. Momentum: RSI oversold/overbought levels, MACD histogram direction and crossovers
3. Volatility: Bollinger Band width and price position within bands
4. Volume: Compare current volume to recent average, volume trend
5. Price Action: Recent candle patterns, support/resistance levels

You MUST respond with ONLY a valid JSON object in this exact format:
{"prediction": "UP" or "DOWN" or "SKIP", "confidence": 0.0 to 1.0, "reasoning": "brief explanation"}

Use "SKIP" only when signals are highly contradictory and there is no clear edge.
Keep reasoning concise (under 200 characters)."""


class AIPredictorService:
    async def predict(self, ai_model: AIModel, market_data: dict, indicators: dict) -> dict:
        try:
            api_key = decrypt_api_key(ai_model.api_key_encrypted)
            
            # Build rich market context
            prompt_parts = [
                f"=== {market_data.get('symbol', 'BTCUSDT')} 5-Minute Analysis ===",
                f"Current Price: {market_data.get('price', 'N/A')}",
                f"24h Change: {market_data.get('price_change_pct', 'N/A')}%",
                f"24h Volume: {market_data.get('volume_24h', 'N/A')} USDT",
                f"24h High: {market_data.get('high_24h', 'N/A')}",
                f"24h Low: {market_data.get('low_24h', 'N/A')}",
                "",
                "--- Recent 5 Candles (oldest to newest) ---",
            ]
            
            # Add recent klines if available
            recent_klines = market_data.get("recent_klines", [])
            for i, k in enumerate(recent_klines[-5:]):
                direction = "▲" if k.get("close_price", 0) >= k.get("open_price", 0) else "▼"
                prompt_parts.append(
                    f"  {direction} O:{k.get('open_price',0):.2f} H:{k.get('high_price',0):.2f} "
                    f"L:{k.get('low_price',0):.2f} C:{k.get('close_price',0):.2f} V:{k.get('volume',0):.1f}"
                )
            
            prompt_parts.extend([
                "",
                "--- Technical Indicators ---",
                f"MACD: {indicators.get('macd', 'N/A')}",
                f"MACD Signal: {indicators.get('macd_signal', 'N/A')}",
                f"MACD Histogram: {indicators.get('macd_hist', 'N/A')}",
                f"RSI(14): {indicators.get('rsi_14', 'N/A')}",
                f"BB Upper: {indicators.get('bb_upper', 'N/A')}",
                f"BB Middle: {indicators.get('bb_middle', 'N/A')}",
                f"BB Lower: {indicators.get('bb_lower', 'N/A')}",
                f"EMA(7): {indicators.get('ema_7', 'N/A')}",
                f"EMA(25): {indicators.get('ema_25', 'N/A')}",
                f"SMA(99): {indicators.get('sma_99', 'N/A')}",
                "",
                "Based on the above data, predict the next 5-minute candle direction. Respond with JSON only."
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
                "max_tokens": 300,
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
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": "AI API request timed out"}
        except httpx.HTTPStatusError as e:
            logger.error(f"AI model {ai_model.name} HTTP error: {e.response.status_code}")
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": f"AI API HTTP error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"AI model {ai_model.name} error: {e}")
            return {"prediction": "SKIP", "confidence": 0.0, "reasoning": f"Error calling AI API: {str(e)}"}
    
    def _parse_response(self, content: str) -> dict:
        """Extract and parse JSON from AI response, handling markdown wrappers."""
        try:
            # Try direct JSON parse first
            parsed = json.loads(content.strip())
        except json.JSONDecodeError:
            # Try extracting from markdown code blocks
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
            except (json.JSONDecodeError, IndexError):
                # Last resort: try to find JSON object with regex-like approach
                try:
                    start = content.index('{')
                    end = content.rindex('}') + 1
                    parsed = json.loads(content[start:end])
                except (ValueError, json.JSONDecodeError):
                    return {"prediction": "SKIP", "confidence": 0.0, "reasoning": f"Failed to parse AI response"}
        
        pred = str(parsed.get("prediction", "SKIP")).upper().strip()
        if pred not in ["UP", "DOWN", "SKIP"]:
            pred = "SKIP"
        
        confidence = parsed.get("confidence", 0.0)
        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except (ValueError, TypeError):
            confidence = 0.0
        
        return {
            "prediction": pred,
            "confidence": confidence,
            "reasoning": str(parsed.get("reasoning", ""))[:500]
        }

ai_predictor_service = AIPredictorService()
