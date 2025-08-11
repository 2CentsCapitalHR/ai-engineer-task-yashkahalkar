from typing import Dict, List, Any
import re
from datetime import datetime
import streamlit as st

class ComplianceChecker:
    def __init__(self):
        self.process_requirements = {
            'Company Incorporation': {
                'required_documents': [
                    'Articles of Association',
                    'Memorandum of Association',
                    'Board Resolution',
                    'UBO Declaration Form'
                ],
                'mandatory_clauses': [
                    'registered office',
                    'share capital', 
                    'directors',
                    'liability',
                    'objects'  # Simplified from 'objects clause'
                ],
                'jurisdiction_requirements': ['ADGM', 'Abu Dhabi Global Market']
            }
        }
        
        self.red_flag_patterns = [
            {
                'pattern': r'UAE Federal Court|Dubai Court',
                'issue': 'Incorrect jurisdiction - should specify ADGM Courts',
                'severity': 'High',
                'category': 'jurisdiction'
            },
            {
                'pattern': r'\[.*\]|TBD|TO BE DETERMINED',
                'issue': 'Template placeholder not filled',
                'severity': 'Medium', 
                'category': 'completeness'
            }
        ]

    def check_document(self, doc_data: Dict[str, Any], process_type: str) -> Dict[str, Any]:
        """HEAVILY DEBUGGED compliance check"""
        print("=" * 80)
        print(f"🔍 STARTING COMPLIANCE CHECK DEBUG")
        print("=" * 80)
        
        # Debug document data
        print(f"📄 Document filename: {doc_data.get('filename', 'UNKNOWN')}")
        print(f"📄 Document type: {doc_data.get('document_type', 'UNKNOWN')}")
        print(f"🔧 Process type: {process_type}")
        
        # CRITICAL: Debug document content
        content = doc_data.get('content', '')
        print(f"📝 Content length: {len(content)} characters")
        print(f"📝 Content preview (first 200 chars): {content[:200]}...")
        print(f"📝 Content preview (last 200 chars): ...{content[-200:]}")
        
        # Check if content is empty
        if not content or len(content.strip()) < 50:
            st.error("❌ CRITICAL: Document content is empty or too short!")
            print("❌ CRITICAL: Document content is empty or too short!")
            return {
                'is_compliant': False,
                'compliance_score': 0,
                'total_issues': 1,
                'positive_matches': 0,
                'issues': [{'issue': 'Document content is empty or unreadable', 'severity': 'High'}],
                'debug_error': 'Empty content'
            }
        
        issues = []
        positive_matches = []
        
        try:
            print("\n🔍 CHECKING MANDATORY CLAUSES...")
            mandatory_results = self._debug_mandatory_clauses(doc_data, process_type)
            issues.extend(mandatory_results['issues'])
            positive_matches.extend(mandatory_results['matches'])
            
            print(f"✅ Mandatory clause results: {len(mandatory_results['issues'])} issues, {len(mandatory_results['matches'])} matches")
            
            print("\n🔍 CHECKING JURISDICTION...")
            jurisdiction_results = self._debug_jurisdiction(doc_data)
            issues.extend(jurisdiction_results['issues'])
            positive_matches.extend(jurisdiction_results['matches'])
            
            print(f"✅ Jurisdiction results: {len(jurisdiction_results['issues'])} issues, {len(jurisdiction_results['matches'])} matches")
            
            print("\n🔍 CHECKING RED FLAGS...")
            red_flag_issues = self._debug_red_flags(doc_data)
            issues.extend(red_flag_issues)
            
            print(f"✅ Red flag results: {len(red_flag_issues)} issues")
            
            print(f"\n📊 TOTAL SUMMARY:")
            print(f"   Issues: {len(issues)}")
            print(f"   Positive matches: {len(positive_matches)}")
            
            # Calculate score with extreme debugging
            compliance_score = self._debug_calculate_score(issues, positive_matches, process_type)
            
            print(f"\n🎯 FINAL COMPLIANCE SCORE: {compliance_score}%")
            print("=" * 80)
            
            return {
                'is_compliant': compliance_score >= 80,
                'compliance_score': compliance_score,
                'total_issues': len(issues),
                'positive_matches': len(positive_matches),
                'issues': issues,
                'debug_info': {
                    'content_length': len(content),
                    'mandatory_matches': len(mandatory_results['matches']),
                    'jurisdiction_matches': len(jurisdiction_results['matches']),
                    'content_preview': content[:100]
                }
            }
            
        except Exception as e:
            print(f"❌ EXCEPTION in compliance check: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'is_compliant': False,
                'compliance_score': 0,
                'total_issues': 0,
                'positive_matches': 0,
                'issues': [{'issue': f'Compliance check failed: {str(e)}', 'severity': 'High'}],
                'error': str(e)
            }

    def _debug_mandatory_clauses(self, doc_data: Dict[str, Any], process_type: str) -> Dict:
        """Debug mandatory clause detection"""
        print(f"🔍 Checking mandatory clauses for process: {process_type}")
        
        issues = []
        matches = []
        
        if process_type not in self.process_requirements:
            print(f"❌ Process type '{process_type}' not recognized!")
            return {'issues': issues, 'matches': matches}
        
        requirements = self.process_requirements[process_type]
        required_clauses = requirements['mandatory_clauses']
        content = doc_data.get('content', '').lower()
        
        print(f"🔍 Required clauses: {required_clauses}")
        print(f"🔍 Searching in content (length: {len(content)})")
        
        for clause in required_clauses:
            # Make detection more flexible
            clause_variations = [
                clause.lower(),
                clause.lower().replace(' ', ''),
                f"{clause.lower()} of",
                f"the {clause.lower()}"
            ]
            
            found = False
            for variation in clause_variations:
                if variation in content:
                    found = True
                    print(f"✅ FOUND: '{clause}' (matched: '{variation}')")
                    matches.append({
                        'category': 'mandatory_clauses',
                        'clause': clause,
                        'content': clause,
                        'found': True,
                        'matched_variation': variation
                    })
                    break
            
            if not found:
                print(f"❌ MISSING: '{clause}' - none of {clause_variations} found in content")
                issues.append({
                    'location': 'Document Content',
                    'issue': f'Missing mandatory clause: {clause}',
                    'severity': 'High',
                    'category': 'mandatory_clauses',
                    'suggestion': f'Add {clause} clause as required for {process_type}'
                })
        
        print(f"🔍 Mandatory clause summary: {len(matches)} found, {len(issues)} missing")
        return {'issues': issues, 'matches': matches}

    def _debug_jurisdiction(self, doc_data: Dict[str, Any]) -> Dict:
        """Debug jurisdiction detection"""
        print(f"🔍 Checking jurisdiction compliance...")
        
        issues = []
        matches = []
        content = doc_data.get('content', '')
        content_lower = content.lower()
        
        # Check for positive ADGM references
        adgm_indicators = [
            'adgm',
            'abu dhabi global market',
            'adgm courts',
            'adgm companies regulations'
        ]
        
        print(f"🔍 Searching for ADGM indicators: {adgm_indicators}")
        
        for indicator in adgm_indicators:
            if indicator.lower() in content_lower:
                print(f"✅ FOUND ADGM indicator: '{indicator}'")
                matches.append({
                    'category': 'jurisdiction',
                    'indicator': indicator,
                    'content': indicator,
                    'found': True
                })
        
        # Check for problematic references
        problematic_refs = ['uae federal court', 'dubai court']
        
        for ref in problematic_refs:
            if ref.lower() in content_lower:
                print(f"❌ FOUND problematic reference: '{ref}'")
                issues.append({
                    'location': 'Jurisdiction Clause',
                    'issue': f'Incorrect jurisdiction reference: {ref}',
                    'severity': 'High',
                    'category': 'jurisdiction',
                    'suggestion': 'Update to specify ADGM as governing jurisdiction'
                })
        
        print(f"🔍 Jurisdiction summary: {len(matches)} positive, {len(issues)} problematic")
        return {'issues': issues, 'matches': matches}

    def _debug_red_flags(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Debug red flag detection"""
        print(f"🔍 Checking for red flags...")
        
        issues = []
        content = doc_data.get('content', '')
        
        for flag in self.red_flag_patterns:
            matches = re.finditer(flag['pattern'], content, re.IGNORECASE)
            match_count = 0
            
            for match in matches:
                match_count += 1
                print(f"❌ RED FLAG: Found '{match.group()}' - {flag['issue']}")
                issues.append({
                    'location': f'Position {match.start()}',
                    'issue': flag['issue'],
                    'severity': flag['severity'],
                    'category': flag['category'],
                    'suggestion': 'Update to comply with ADGM requirements',
                    'matched_text': match.group()
                })
            
            if match_count == 0:
                print(f"✅ No matches for red flag pattern: {flag['pattern']}")
        
        print(f"🔍 Red flag summary: {len(issues)} issues found")
        return issues

    def _debug_calculate_score(self, issues: List[Dict], positive_matches: List[Dict], process_type: str) -> float:
        """Debug score calculation with detailed logging"""
        print(f"\n🔍 CALCULATING COMPLIANCE SCORE...")
        print(f"   Input issues: {len(issues)}")
        print(f"   Input positive matches: {len(positive_matches)}")
        
        category_weights = {
            'jurisdiction': 25,
            'mandatory_clauses': 25,
            'document_type': 15,
            'formatting': 15,
            'signatures': 10,
            'red_flags': 10
        }
        
        total_score = 0
        
        for category, max_points in category_weights.items():
            category_issues = [issue for issue in issues if issue.get('category') == category]
            category_matches = [match for match in positive_matches if match.get('category') == category]
            
            print(f"\n🔍 Category: {category} (max {max_points} points)")
            print(f"   Issues: {len(category_issues)}")
            print(f"   Matches: {len(category_matches)}")
            
            if category == 'jurisdiction':
                adgm_found = any('adgm' in str(match.get('content', '')).lower() 
                               for match in category_matches)
                if adgm_found:
                    points = max_points
                    print(f"   ✅ ADGM found - awarding {points} points")
                elif category_issues:
                    points = 0
                    print(f"   ❌ Issues found - awarding 0 points")
                else:
                    points = max_points * 0.5
                    print(f"   ⚠️ No clear indication - awarding {points} points")
                total_score += points
                
            elif category == 'mandatory_clauses':
                required_clauses = self.process_requirements.get(process_type, {}).get('mandatory_clauses', [])
                if required_clauses:
                    percentage = min(len(category_matches) / len(required_clauses), 1.0)
                    points = max_points * percentage
                    print(f"   📊 Found {len(category_matches)}/{len(required_clauses)} clauses - awarding {points} points")
                else:
                    points = max_points
                    print(f"   ✅ No requirements - awarding {points} points")
                total_score += points
                
            else:
                if category_issues:
                    points = 0
                    print(f"   ❌ Has issues - awarding 0 points")
                else:
                    points = max_points
                    print(f"   ✅ No issues - awarding {points} points")
                total_score += points
        
        final_score = min(max(total_score, 0), 100)
        print(f"\n🎯 SCORE CALCULATION COMPLETE:")
        print(f"   Total raw score: {total_score}")
        print(f"   Final score (0-100): {final_score}")
        
        return final_score

    def generate_compliance_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed compliance report"""
        return f"""
ADGM COMPLIANCE ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL COMPLIANCE STATUS: {'COMPLIANT' if results['is_compliant'] else 'NON-COMPLIANT'}
Compliance Score: {results['compliance_score']:.1f}%
Total Issues Found: {results['total_issues']}
Total Positive Matches: {results.get('positive_matches', 0)}

DEBUG INFO:
- Content Length: {results.get('debug_info', {}).get('content_length', 'Unknown')}
- Mandatory Matches: {results.get('debug_info', {}).get('mandatory_matches', 0)}
- Jurisdiction Matches: {results.get('debug_info', {}).get('jurisdiction_matches', 0)}
        """
