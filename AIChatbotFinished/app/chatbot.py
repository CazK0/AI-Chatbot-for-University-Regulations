import os
import re
from datetime import datetime
from app.pdf_policy_loader import BirminghamPolicyLoader
from app.qa_service import answer_query


class UniversityChatbot:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        self.policy_loader = BirminghamPolicyLoader()
        self.conversation_context = []

    def _extract_query_intent(self, user_message):
        message_lower = user_message.lower()

        if any(term in message_lower for term in ['fail', 'failed', 'failing']):
            numbers = re.findall(r'\b(\d+)\b', message_lower)
            module_count = int(numbers[0]) if numbers else None

            is_postgraduate = any(term in message_lower for term in
                                  ['master', 'masters', 'postgraduate', 'pg', 'msc', 'ma', 'mres',
                                   'taught postgraduate'])
            is_undergraduate = any(
                term in message_lower for term in ['undergraduate', 'bachelor', 'bsc', 'ba', 'undergrad'])

            return {
                'intent': 'failure_query',
                'module_count': module_count,
                'is_soft_fail': 'soft' in message_lower,
                'is_hard_fail': 'hard' in message_lower,
                'is_postgraduate': is_postgraduate,
                'is_undergraduate': is_undergraduate,
                'specific_scenario': True
            }

        elif any(term in message_lower for term in
                 ['progress', 'progression', 'next year', 'advance', 'graduate', 'graduation']):
            is_postgraduate = any(
                term in message_lower for term in ['master', 'masters', 'postgraduate', 'pg', 'msc', 'ma', 'mres'])
            is_undergraduate = any(
                term in message_lower for term in ['undergraduate', 'bachelor', 'bsc', 'ba', 'undergrad'])
            return {
                'intent': 'progression_query',
                'is_postgraduate': is_postgraduate,
                'is_undergraduate': is_undergraduate,
                'specific_scenario': True
            }

        elif any(term in message_lower for term in ['appeal', 'appeals', 'appealing']):
            return {'intent': 'appeals_query', 'specific_scenario': True}

        elif any(term in message_lower for term in ['resit', 'retake', 'reassess']):
            return {'intent': 'resit_query', 'specific_scenario': True}

        return {'intent': 'general', 'specific_scenario': False}

    def _build_enhanced_prompt(self, user_message, policy_context, query_intent):
        base_info = """You are a helpful University of Birmingham student support chatbot. You provide accurate, specific information about university policies and procedures.

CRITICAL UNIVERSITY OF BIRMINGHAM REGULATIONS:

PASS MARKS & FAILURE DEFINITIONS:
- Undergraduate modules (Levels C, I, H): 40% pass mark
- Postgraduate modules (Level M): 50% pass mark  
- Hard fail: Below 40% (regardless of programme level)
- Soft fail: 40-49% (below programme pass mark but above hard fail threshold)

FAILURE LIMITS & GRADUATION RULES:
MASTER'S/POSTGRADUATE TAUGHT PROGRAMMES:
- Can soft fail up to 2 modules (40-49% marks) and still graduate
- Cannot hard fail any modules (must achieve 40%+ in all modules)
- Must achieve 50% overall weighted average to graduate
- Soft failed modules do NOT need to be resit if overall average is 50%+

UNDERGRADUATE PROGRAMMES:  
- Can hard fail 1 module (below 40%) AND soft fail 1 module (40-49%) to still graduate
- Pass mark: 40% - must achieve this in modules to get credit
- Need 100+ credits minimum to progress to next year (out of 120 credits typically)
- Failed modules: No credit awarded until passed

RESIT RULES:
- One opportunity to retrieve failure via reassessment or repetition
- Resit marks capped at pass mark for degree classification  
- Must resit within one year of initial failure typically

PROGRESSION REQUIREMENTS:
- Undergraduate: 100+ credits to progress (each module typically 20 credits)
- Stage contributions: Stage 1 (0%), Stage 2 (25%), Stage 3 (75%)
- Postgraduate: Must complete all required modules and dissertation

DEGREE CLASSIFICATIONS:
- First Class: 70%+, 2:1: 60-69%, 2:2: 50-59%, Third: 40-49%
- Master's: Pass, Merit (60%+), Distinction (70%+)

APPEALS PROCESS:
- Deadline: 10 working days from results release
- Evidence-based process requiring third-party documentation
- Cannot appeal just disagreeing with marks - need procedural issues or unknown circumstances"""

        if query_intent['intent'] == 'failure_query' and query_intent.get('module_count'):
            count = query_intent['module_count']
            is_postgrad = query_intent.get('is_postgraduate', False)
            is_undergrad = query_intent.get('is_undergraduate', False)
            is_soft_fail = query_intent.get('is_soft_fail', False)
            is_hard_fail = query_intent.get('is_hard_fail', False)

            if is_postgrad:
                specific_info = f"""
SPECIFIC SCENARIO - MASTER'S PROGRAMME FAILING {count} MODULES:
Master's Programme Failure Rules:
- Can soft fail up to 2 modules (40-49% - below pass mark but above hard fail threshold)
- Cannot hard fail any modules (below 40%)
- Pass mark for Master's modules (Level M): 50%

Your scenario - {count} module(s) failed:
"""
                if is_soft_fail and count <= 2:
                    specific_info += f"✓ CAN GRADUATE: Soft failing {count} module(s) is allowed\n- Can graduate if overall weighted average is 50% or above\n- No need to resit if overall average requirement is met\n- If overall average below 50%, must resit failed modules to improve average"
                elif is_soft_fail and count > 2:
                    specific_info += f"✗ EXCEEDS LIMIT: Soft failing {count} modules exceeds maximum (only 2 soft fails allowed)\n- Must resit excess failed modules to bring total soft fails to 2 or fewer\n- Then check if 50% overall average achieved to graduate"
                elif is_hard_fail:
                    specific_info += f"✗ NOT ALLOWED: Hard failing any modules on Master's programmes is not permitted\n- Must resit all hard failed modules to achieve at least 40%\n- After resits, can have max 2 soft fails and need 50% overall average to graduate"
                else:
                    specific_info += f"Failing {count} module(s) impact:\n- If soft fails (40-49%): {'Can graduate if overall average 50%+' if count <= 2 else 'Exceeds 2-module limit'}\n- If hard fails (below 40%): Must resit to achieve 40%+ in all modules"

            elif is_undergrad:
                specific_info = f"""
SPECIFIC SCENARIO - UNDERGRADUATE PROGRAMME FAILING {count} MODULES:
Undergraduate Programme Failure Rules:
- Can hard fail up to 1 module (below 40%) AND soft fail up to 1 module (40-49%)
- OR soft fail multiple modules if no hard fails
- Pass mark for undergraduate modules (Levels C, I, H): 40%
- Need 100+ credits to progress (typically 6 modules × 20 credits = 120 per year)

Your scenario - {count} module(s) failed:
"""
                credits_failed = count * 20
                credits_passed = 120 - credits_failed

                if count == 1:
                    if is_hard_fail:
                        specific_info += f"✓ ALLOWED: 1 hard fail is within limits\n- Can still graduate if it's your only failure\n- {credits_passed} credits achieved, {'CAN PROGRESS' if credits_passed >= 100 else 'CANNOT PROGRESS'} (need 100 minimum)"
                    elif is_soft_fail:
                        specific_info += f"✓ ALLOWED: 1 soft fail is within limits\n- Can still graduate\n- {credits_passed} credits achieved, {'CAN PROGRESS' if credits_passed >= 100 else 'CANNOT PROGRESS'} (need 100 minimum)"
                elif count == 2:
                    specific_info += f"DEPENDS on failure types:\n- 1 hard fail + 1 soft fail: ✓ ALLOWED to graduate\n- 2 hard fails: ✗ EXCEEDS LIMIT\n- 2 soft fails: May be allowed depending on programme\n- {credits_passed} credits achieved, {'CAN PROGRESS' if credits_passed >= 100 else 'CANNOT PROGRESS'} (need 100 minimum)"
                else:
                    specific_info += f"✗ EXCEEDS LIMITS: {count} failed modules likely exceeds graduation requirements\n- {credits_passed} credits achieved, CANNOT PROGRESS (need 100 minimum)\n- Must resit failed modules before progression"
            else:
                specific_info = f"""
SPECIFIC SCENARIO - FAILING {count} MODULES:
Programme type not specified. General Birmingham University rules:

MASTER'S PROGRAMMES:
- Can soft fail up to 2 modules (40-49%) and still graduate if 50% overall average achieved
- Cannot hard fail any modules (below 40%)
- Pass mark: 50% per module, but 50% overall average sufficient for graduation

UNDERGRADUATE PROGRAMMES:
- Can hard fail 1 module AND soft fail 1 module to still graduate
- Pass mark: 40%
- Need 100+ credits to progress

Your scenario needs programme specification for precise guidance."""

        elif query_intent['intent'] == 'progression_query':
            is_postgrad = query_intent.get('is_postgraduate', False)
            is_undergrad = query_intent.get('is_undergraduate', False)

            if is_postgrad:
                specific_info = """
MASTER'S PROGRAMME PROGRESSION/GRADUATION RULES:
- Can soft fail up to 2 modules (40-49%) and still graduate
- Hard fail allowance: None (must achieve 40%+ in all modules)  
- KEY REQUIREMENT: Must achieve 50% overall weighted average to graduate
- Soft fails don't require resit if 50% overall average achieved
- Must complete dissertation component (60 credits at Level M)
- Total credits required: 180 credits typically
- Merit: 60%+ weighted average, Distinction: 70%+ weighted average"""
            elif is_undergrad:
                specific_info = """
UNDERGRADUATE PROGRESSION RULES:
- Need 100 credits minimum to progress to next year (out of 120 credits typically)
- Can hard fail 1 module + soft fail 1 module and still graduate
- Stage contributions to final degree: Stage 1 (0%), Stage 2 (25%), Stage 3 (75%)
- Degree classifications: First (70%+), 2:1 (60-69%), 2:2 (50-59%), Third (40-49%)
- Pass mark: 40% for undergraduate modules (Levels C, I, H)
- Failed modules get one resit opportunity (marks capped at pass mark)"""
            else:
                specific_info = """
GENERAL PROGRESSION RULES:
Please specify if you're asking about undergraduate or postgraduate/master's programmes as the rules differ significantly.

UNDERGRADUATE: Need 100+ credits, can fail up to 2 modules under certain conditions
POSTGRADUATE: Must pass all modules, soft fail allowance for up to 2 modules on Master's"""

        elif query_intent['intent'] == 'appeals_query':
            specific_info = """
APPEALS SPECIFIC INFORMATION:
- Deadline: 10 working days from results release on Student Gateway
- Grounds: (1) Circumstances unknown to Board of Examiners, (2) Administrative irregularity
- Cannot appeal: Just disagreeing with marks received
- Evidence required: Must support all claims with independent third-party evidence
- Process: School response → Academic Appeal Committee review → possible hearing
- Timeline: 8-10 weeks during summer appeals period
- Outcome options: Confirm School decision, reject appeal, or refer to hearing"""

        elif query_intent['intent'] == 'resit_query':
            specific_info = """
RESIT SPECIFIC RULES:
- One opportunity to retrieve failure via reassessment or repetition
- Reassessment: Complete further assessment as specified by Board of Examiners
- Repetition: Attend all teaching sessions and complete all assessments
- Mark capping: Resit marks capped at pass mark for degree classification
- Timeline: Usually provided within one year of initial failure
- External students: May have limited access to University resources during resits"""

        else:
            specific_info = ""

        return f"""{base_info}

{specific_info}

{policy_context}

INSTRUCTIONS: 
- Give specific, direct answers using the regulations above
- For failure scenarios, clearly state whether allowed/not allowed and explain consequences  
- Always mention students can contact their School office for personalized advice
- Be precise about numbers, deadlines, and procedures
- Distinguish between undergraduate and postgraduate rules when relevant

Student Question: {user_message}

Provide a helpful, accurate response:"""

    def process_message(self, user_message):
        try:
            self.conversation_context.append({
                'timestamp': datetime.now(),
                'user_message': user_message,
                'type': 'user'
            })

            query_intent = self._extract_query_intent(user_message)
            response = self._get_google_response(user_message, query_intent)

            self.conversation_context.append({
                'timestamp': datetime.now(),
                'bot_response': response,
                'type': 'bot'
            })
            return response
        except Exception as e:
            return "I encountered an error processing your request. Please try again."

    def _get_google_response(self, user_message, query_intent):
        policy_context = ""
        try:
            search_results = self.policy_loader.search_policies(user_message)
            if search_results:
                policy_context = "\n\nRelevant Birmingham Policy Information:\n"
                for result in search_results:
                    policy_context += f"\nFrom {result['policy_name']}:\n"
                    for section in result['content_sections']:
                        policy_context += f"{section[:800]}...\n"
        except Exception as e:
            pass

        full_prompt = self._build_enhanced_prompt(user_message, policy_context, query_intent)

        try:
            response = answer_query(full_prompt)
            if response and not response.startswith("Error:"):
                return response
            else:
                return "I couldn't generate a proper response. Please try again."
        except Exception as e:
            return "I'm having trouble connecting to my AI service. Please try again in a moment."

    def health_check(self):
        return {
            'google_ai_available': True,
            'api_key_present': bool(os.environ.get("GOOGLE_API_KEY")),
            'pdf_loader_available': self.policy_loader is not None
        }