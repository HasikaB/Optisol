import logging
import os
import json
import requests
import re
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class AIProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_token = os.getenv('hugging_face')
        if not self.api_token:
            self.logger.error(" Hugging Face API token not found in environment.")
        else:
            self.logger.info(" Hugging Face API token loaded successfully.")

    def _extract_json(self, text):
        """Extract the first valid JSON object from AI text."""
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  
            r'\{.*?\}',  
        ]
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue
        return None

    def _format_web_results(self, results):
        """Format web results for AI context and chart generation."""
        if not results:
            return ""
        formatted = ""
        for i, r in enumerate(results[:5], 1):
            formatted += f"{i}. {r.get('title','')}\n   Source: {r.get('source','')}\n   {r.get('description','')}\n"
        return formatted

    def _generate_chart(self, title, data=None):
        """Generate a simple line chart and return as base64 string."""
        if not data:
            data = [1, 2, 2, 3, 4, 5]  
        fig, ax = plt.subplots()
        ax.plot(data, marker='o')
        ax.set_title(title)
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    def _create_fallback_structure(self, topic, document_text="", web_results=None):
        """Fallback report with charts."""
        summary = f"Analysis of {topic}"
        if document_text:
            summary += f". Document provided with {len(document_text)} characters."
        if web_results:
            summary += f" {len(web_results)} web sources analyzed."

        findings = []
        if document_text:
            findings.append(f"Document contains information about {topic}")
        if web_results:
            for r in web_results[:3]:
                findings.append(f"Reference: {r.get('title','Source')}")

        charts = [
            self._generate_chart(f"{topic} Trend 1"),
            self._generate_chart(f"{topic} Trend 2")
        ]

        return {
            "executive_summary": summary,
            "key_findings": findings if findings else ["Processing complete"],
            "charts": charts,
            "recommendations": ["Review the provided sources", "Consider additional research"]
        }

    def generate_report_structure(self, topic, document_text="", web_results=None):
        """Generate structured report using Bloomz-560m via Hugging Face API."""
        if not self.api_token:
            self.logger.warning(" Hugging Face API token missing. Using fallback report.")
            return self._create_fallback_structure(topic, document_text, web_results)

        try:
            doc_excerpt = document_text[:600] if document_text else ""
            web_context = self._format_web_results(web_results)

            prompt = (
                f"Generate a JSON report about the topic: {topic}.\n\n"
                f"Include keys: executive_summary (string), key_findings (list), "
                f"charts (list), recommendations (list). Only return valid JSON.\n\n"
                f"Document excerpt: {doc_excerpt}\n"
                f"{web_context}\n"
            )

            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/bigscience/bloomz-560m",
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.3}},
                timeout=30
            )

            if response.status_code != 200:
                self.logger.error(f"❌ Hugging Face API error: {response.status_code} {response.text}")
                return self._create_fallback_structure(topic, document_text, web_results)

            result = response.json()
            generated_text = (
                result[0]["generated_text"]
                if isinstance(result, list) and "generated_text" in result[0]
                else str(result)
            )

            self.logger.info(f"📝 AI output: {generated_text[:200]}...")

            parsed = self._extract_json(generated_text)
            if not parsed:
                self.logger.warning("⚠️ AI did not return valid JSON. Using fallback.")
                return self._create_fallback_structure(topic, document_text, web_results)

            # Ensure all fields exist
            validated = {
                "executive_summary": str(parsed.get("executive_summary", f"Analysis of {topic}"))[:1000],
                "key_findings": parsed.get("key_findings", []) or ["See executive summary for key findings"],
                "charts": parsed.get("charts", []) or [
                    self._generate_chart(f"{topic} Trend 1"),
                    self._generate_chart(f"{topic} Trend 2")
                ],
                "recommendations": parsed.get("recommendations", []) or ["See executive summary for recommendations"]
            }

            # Limit items for frontend
            for key in ["key_findings", "charts", "recommendations"]:
                validated[key] = validated[key][:5]

            self.logger.info(f"✅ Report generated with {len(validated['key_findings'])} findings and {len(validated['charts'])} charts")
            return validated

        except Exception as e:
            self.logger.error(f"AI processing error: {e}", exc_info=True)
            return self._create_fallback_structure(topic, document_text, web_results)
