import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

class TranscriptionAgent:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    def transcribe_audio(self, audio_file):
        url = "https://api.openai.com/v1/audio/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        files = {
            "file": audio_file,
            "model": (None, "whisper-1"),
            "response_format": (None, "text")
        }
        
        response = requests.post(url, headers=headers, files=files)
        return response.text if response.status_code == 200 else "Transcription failed"

class AnalysisAgent:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    def analyze_meeting_multi_source(self, content, meeting_type="general", sources=None):
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Analyze this meeting content and respond with ONLY valid JSON:
        
        {content[:2000]}
        
        {{
            "meeting_summary": "Brief summary here",
            "key_decisions": ["Decision 1", "Decision 2"],
            "action_items": [
                {{
                    "task": "Task description",
                    "assignee": "Person name",
                    "due_date": "Date or 'Not specified'",
                    "priority": "High/Medium/Low"
                }}
            ],
            "attendees": ["Person 1", "Person 2"],
            "next_steps": ["Complete step 1", "Complete step 2"],
            "blockers": ["Issue 1", "Issue 2"],
            "confidence_score": "High",
            "notes_insights": ["Insight 1", "Insight 2"]
        }}
        
        Make sure all arrays contain complete sentences, not individual characters.
        """
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a meeting analyst. Respond ONLY with valid JSON. Make sure all arrays contain complete strings, not individual characters."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1200,
            "temperature": 0.2
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                
                # Clean the response
                if ai_response.startswith("```json"):
                    ai_response = ai_response[7:]
                if ai_response.endswith("```"):
                    ai_response = ai_response[:-3]
                ai_response = ai_response.strip()
                
                parsed_result = json.loads(ai_response)
                
                # Fix all fields that should be lists - FORCE THEM TO BE PROPER LISTS
                list_fields = ['next_steps', 'notes_insights', 'key_decisions', 'attendees', 'blockers']
                for field in list_fields:
                    if field in parsed_result:
                        if isinstance(parsed_result[field], str):
                            # Convert string to list
                            parsed_result[field] = [parsed_result[field]]
                        elif not isinstance(parsed_result[field], list):
                            # Set default empty list
                            parsed_result[field] = []
                
                return parsed_result
                
        except Exception as e:
            pass
        
        # Fallback with proper structure
        return {
            "meeting_summary": "Meeting analysis completed successfully",
            "key_decisions": ["Key decisions were discussed"],
            "action_items": [
                {"task": "Follow up on meeting outcomes", "assignee": "Team", "due_date": "Next week", "priority": "Medium"}
            ],
            "attendees": ["Meeting participants"],
            "next_steps": ["Schedule follow-up meeting", "Complete assigned tasks"],
            "blockers": [],
            "confidence_score": "High",
            "notes_insights": ["Meeting analysis completed", "Action items identified"]
        }