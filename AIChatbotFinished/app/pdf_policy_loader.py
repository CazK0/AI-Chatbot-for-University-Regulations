import os
import re
from typing import List, Dict, Optional
import requests
from urllib.parse import urlparse


class BirminghamPolicyLoader:
    def __init__(self):
        self.documents = {}
        self.document_urls = {
            'regulations_2025_section_1': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-1.pdf',
            'regulations_2025_section_2': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-2.pdf',
            'regulations_2025_section_3': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-3.pdf',
            'regulations_2025_section_4': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-4.pdf',
            'regulations_2025_section_5': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-5.pdf',
            'regulations_2025_section_6': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-6.pdf',
            'regulations_2025_section_7': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-7.pdf',
            'regulations_2025_section_8': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-8.pdf',
            'regulations_2025_section_9': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/legislation/documents/public/cohort-legislation-2025-26/regulations-25-26-section-9.pdf',
            'appeals_faq': 'https://intranet.birmingham.ac.uk/student/academic-support/registry/documents/public/student-conduct-complaints-and-appeals/student-appeals-documents/appeals-faq-261kb.pdf',
        }
        self.static_content = {
            'regulations_2025_section_1': {
                'title': 'Birmingham Regulations Section 1 - Definitions and Interpretation (2025-26)',
                'content': '''
KEY DEFINITIONS (2025-26):
- Academic Misconduct: Plagiarism (serious), examination irregularities, conduct giving unfair advantage in exams/assessed work
- Award: Degree, diploma, certificate or formal recognition of programme completion
- Board of Examiners: Body determining results, marks, weighted mean marks, degree classifications, grade point averages, makes recommendations to Progress Board
- External Student: Student not requiring instruction but granted assessment opportunities; limited access to resources as determined by University
- Friend: University staff member, registered student, Sabbatical Officer of Guild, or Guild Advisor
- Graduand: Student officially notified of meeting award requirements but not yet had award conferred
- Leave of Absence: Recognised authorised break from studies per Code of Practice
- Registered Student: Person currently registered for instruction in the University
- Programme Requirements: Rules regarding modules and assessments for degree completion
- Programme Specification: Statement of learning outcomes, teaching methods, assessment methods, module relationships
- Progress and Awards Board of Senate: Body with delegated responsibility for progression and degree classification decisions
- Registration: Process recording applicant as Registered Student, entitling instruction for University Session
- University Session: Period of learning, teaching and assessment (31 weeks for standard session)

INTERPRETATION RULES:
- Regulations interpreted not to conflict with Charter or Statutes
- Interpretation Act 1978 applies to University Legislation
- Singular includes plural, masculine includes feminine  
- University Legislation applies to all members of the University
                '''
            },

            'regulations_2025_section_7': {
                'title': 'Birmingham Regulations Section 7 - Assessment, Progression and Award (2025-26)',
                'content': '''
ASSESSMENT RULES (2025-26):
- Pass marks: 40% for levels F, C, I, H modules; 50% for level M and D modules
- Module assessment generates single mark 0-100 or pass/fail
- Credit awarded only for successful completion of stated learning outcomes
- Marks provisional until confirmed by Board of Examiners

FAILURE IN ASSESSMENT:
- Failed students get ONE opportunity to retrieve failure via re-assessment or repetition
- Normally provided within one year of initial failure
- Re-assessment: Complete further assessment as specified by Board of Examiners
- Repetition: Attend all teaching sessions and complete all assessment requirements
- Mark after successful retrieval capped at pass mark for degree classification
- Higher of two fail marks used if student fails the retrieval attempt

PROGRESSION REQUIREMENTS (UNDERGRADUATE):
- Need 100 credits minimum at given stage to progress to subsequent stage
- Standard: 120 credits per University Session (6 modules × 20 credits typically)
- Failed credits may need redemption even if progression allowed
- Stage contributions to degree: Stage 1 (0%), Stage 2 (25%), Stage 3 (75%)
- For Undergraduate Masters: Stage 1 (0%), Stage 2 (20%), Stage 3 (80%)

DEGREE CLASSIFICATION BOUNDARIES:
- Class I: 70 or above
- Class IIi (2:1): 60-69  
- Class IIii (2:2): 50-59
- Class III: 40-49
- Pass degree: Less than 300 credits but merits degree award

AWARD REQUIREMENTS:
- Bachelor's degree (360 credits): At least 320 credits including 100+ at level C, 200+ at levels I&H with 100+ at level H
- Bachelor's with honours (480 credits): At least 440 credits with specified level distributions
- Undergraduate Master's: At least 440 credits including 100+ at level M, stage 2 average 55+

EXTENUATING CIRCUMSTANCES:
- Board of Examiners may consider illness/adverse circumstances via EC procedures  
- Student responsibility to bring circumstances to Board's attention before meeting
- May award classification consistent with judged performance without circumstances
- Marks not normally adjusted - reflect actual performance
- Additional retrieval attempt may be granted if failure due to extenuating circumstances
                '''
            },

            'regulations_2025_section_5': {
                'title': 'Birmingham Regulations Section 5 - Admission and Registration (2025-26)',
                'content': '''
REGISTRATION REQUIREMENTS (2025-26):
- Must complete registration before commencing programme
- Annual registration required until programme completion
- Must declare obedience to University Legislation on registration
- Full-time students: cannot simultaneously attend other full-time programmes
- Must provide documentary evidence of right to study in UK

ATTENDANCE PATTERNS:
- Standard University Session: 31 weeks learning/teaching/assessment (Autumn, Spring, Summer terms)
- Undergraduate full-time: 120 credits per session standard pattern
- Postgraduate taught full-time: up to 180 credits per session (40+ hours/week over 45 weeks)
- May be required to attend outside University Session for some programmes

FEES AND PAYMENT:
- Tuition fees payable on registration unless Direct Debit instalments elected
- Non-refundable 1% interest charge on instalment plans over £9,500
- Fees calculated pro-rata for students repeating part of programme
- Student responsible for payment regardless of third-party invoicing arrangements

NON-PAYMENT CONSEQUENCES:
- Default interest: £50 or 1.5% whichever greater
- Exclusion from University following appropriate reminder letters
- Excluded students cannot: have work marked, receive marks/feedback, progress to next stage, receive awards, participate in graduation
- Imposed Leave of Absence may be applied stopping all academic engagement
- 12 months continuous exclusion = automatic withdrawal

VISA REQUIREMENTS:
- Must have appropriate visa reflecting circumstances, programme and study mode
- Must inform University immediately of any changes to UK study rights
- University sponsorship may be withdrawn for visa non-compliance
- Academic Registrar may withdraw student for invalid/inappropriate visa status

IDENTITY CARDS:
- Issued on registration at commencement of studies
- Remains University property, may be withdrawn for good reason
- Personal use only - no lending to others
- Must be surrendered when ceasing to be Registered Student
- Required for identity confirmation when requested
                '''
            },

            'regulations_2025_section_8': {
                'title': 'Birmingham Regulations Section 8 - Student Conduct (2025-26)',
                'content': '''
STUDENT CONDUCT SCOPE (2025-26):
- Applies to all Registered Students, Leave of Absence, Thesis Awaited Status, External Resit Students, Graduands
- Covers conduct regardless of location (on/off University premises, electronic communication)
- University normally acts when: misconduct against student/staff, against visitors on premises, during University activities
- Wider scope for Fitness to Practise students (must comply with Professional Conduct codes)

DISCIPLINARY OFFENCES:
- Breach of University Statutes, Ordinances, Regulations, Codes of Practice
- Violent, indecent, disorderly, threatening, intimidating, offensive behaviour/language
- Sexual misconduct including unwanted touching, kissing, sexual acts, intercourse
- Harassment, bullying, coercion of students, staff, visitors
- Fraud, deceit, deception, dishonesty related to University, programmes, procedures
- Theft, misappropriation, misuse of University/others' property
- Academic Misconduct: serious plagiarism, examination irregularities, unfair advantage conduct
- Conduct bringing University into disrepute
- Unauthorised use/damage to University premises/property
- Action likely to cause injury/impair safety on premises
- Criminal offences, police cautions, community resolution orders
- Failure to disclose identity to University staff when reasonably required
- Controlled drug/psychoactive substance offences on University property

INVESTIGATION PROCESS:
- Investigating Officer nominated by Academic Registrar (or Head of College for plagiarism/Fitness to Practise)
- Student informed in writing of alleged breaches, invited to fact-finding meeting
- May be accompanied by Friend as defined in Regulations
- Matter may be dealt with via low-level sanctions if student admits offence and consents

LOW-LEVEL SANCTIONS:
- Formal written warning
- Community Service (18+ only, with consent)
- Behavioural agreement/support engagement
- Making good any damage/repair costs
- Exclusion from/restriction of University residences up to 12 months

TEMPORARY RESTRICTIONS/SUSPENSION:
- Academic Registrar may impose immediate temporary restrictions/suspension for:
  - Reasonable suspicion of serious disciplinary offence
  - Charges/investigation for serious criminal offence
  - Health grounds posing danger to self/others
- Initial period: up to 3 months, may be extended
- Student may appeal within 15 working days to Pro-Vice-Chancellor (Education)
- Regular reviews required, student may make representations
                '''
            },

            'appeals_faq': {
                'title': 'Student Appeals FAQ (Current)',
                'content': '''
APPEALS PROCESS:
- Definition: Submissions seeking amendment/reversal of Board of Examiners decisions due to academic performance
- Deadline: 10 University working days from results release on Student Gateway
- Cannot appeal: Dissatisfaction with marks or believing you deserve higher marks

GROUNDS FOR APPEAL:
1. Circumstances unknown to Board of Examiners that affected academic performance
2. Administrative irregularity or procedural failure creating reasonable doubt
3. (Postgraduate Research only) Bias in thesis assessment

EVIDENCE REQUIREMENTS:
- Appeals are evidence-based requiring independent third-party evidence
- Medical grounds need signed certificates on headed paper
- Evidence in foreign languages must be translated to English
- Evidence must show impact of circumstances and be relevant to cited period

PROCESS TIMELINE:
- 8-10 weeks during main summer appeals period (July-October)
- Form forwarded to School for response
- Academic Appeal Committee consideration
- Possible referral to hearing if more information needed

HEARING DETAILS:
- Panel of 3 academic staff + student representative
- Student and School representative invited to attend
- Friend can accompany (staff member, student, Guild officer/advisor)
- Can proceed in absence, send statement, or send Friend to represent

OUTCOMES & PROGRESSION:
- Can continue studies in temporary attendance (at School discretion)
- Need 100+ credits for progression to next year
- Can defer graduation until appeal resolved (next opportunity in December if defer summer)
- If appeal changes degree classification, must return original certificates

TYPES OF ASSESSMENT ATTEMPTS:
- Sit/First attempt: No mark capping, as if first time due to extenuating circumstances
- Re-sit: Mark capped at pass mark for degree classification
- Repeat: Complete all module assessments and attend teaching, mark may be capped

STUDENT STATUS CHANGES:
- Internal Student: Full campus access, attend teaching, pay fees
- External Student: Library and Canvas access, no teaching, no fees
                '''
            }
        }

    def load_all_policies(self):
        for doc_id, content_data in self.static_content.items():
            self.documents[doc_id] = {
                'title': content_data['title'],
                'content': content_data['content'],
                'sections': self._split_into_sections(content_data['content'])
            }

    def _split_into_sections(self, content: str) -> List[str]:
        sections = []
        paragraphs = content.strip().split('\n\n')

        for paragraph in paragraphs:
            if paragraph.strip():
                if len(paragraph) > 500:
                    sentences = paragraph.split('. ')
                    current_section = ""
                    for sentence in sentences:
                        if len(current_section + sentence) > 400:
                            if current_section:
                                sections.append(current_section.strip())
                            current_section = sentence + ". "
                        else:
                            current_section += sentence + ". "
                    if current_section:
                        sections.append(current_section.strip())
                else:
                    sections.append(paragraph.strip())

        return sections

    def search_policies(self, query: str, max_results: int = 5) -> List[Dict]:
        if not self.documents:
            self.load_all_policies()

        query_lower = query.lower()
        query_terms = re.findall(r'\b\w+\b', query_lower)

        results = []

        for doc_id, doc_data in self.documents.items():
            matching_sections = []

            for section in doc_data['sections']:
                section_lower = section.lower()
                relevance_score = 0
                for term in query_terms:
                    if term in section_lower:
                        relevance_score += section_lower.count(term)
                if len(query_terms) > 1:
                    query_phrase = ' '.join(query_terms)
                    if query_phrase in section_lower:
                        relevance_score += 5
                key_terms = {
                    'appeal': 3, 'fail': 3, 'progression': 3, 'credit': 2,
                    'resit': 3, 'deadline': 2, 'evidence': 2, 'hearing': 2
                }

                for key_term, boost in key_terms.items():
                    if key_term in section_lower:
                        relevance_score += boost

                if relevance_score > 0:
                    matching_sections.append({
                        'section': section,
                        'score': relevance_score
                    })

            if matching_sections:
                matching_sections.sort(key=lambda x: x['score'], reverse=True)
                top_sections = [s['section'] for s in matching_sections[:3]]

                results.append({
                    'policy_name': doc_data['title'],
                    'content_sections': top_sections,
                    'total_score': sum(s['score'] for s in matching_sections[:3])
                })
        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results[:max_results]

    def get_document_content(self, doc_id: str) -> Optional[Dict]:
        if not self.documents:
            self.load_all_policies()
        return self.documents.get(doc_id)

    def add_document_content(self, doc_id: str, title: str, content: str):
        self.static_content[doc_id] = {
            'title': title,
            'content': content
        }
        if self.documents:
            self.documents[doc_id] = {
                'title': title,
                'content': content,
                'sections': self._split_into_sections(content)
            }

    def list_available_documents(self) -> List[str]:
        if not self.documents:
            self.load_all_policies()
        return list(self.documents.keys())

    def get_document_summary(self) -> Dict[str, str]:
        if not self.documents:
            self.load_all_policies()

        summary = {}
        for doc_id, doc_data in self.documents.items():
            word_count = len(doc_data['content'].split())
            section_count = len(doc_data['sections'])
            summary[doc_id] = f"{doc_data['title']} ({word_count} words, {section_count} sections)"

        return summary