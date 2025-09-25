#!/usr/bin/env python3
"""
Comprehensive Testing Script for Intelligent Text-Based Chatbot
This script tests all aspects of the chatbot functionality and performance.
"""

import sys
import os
import requests
import json
import time
import unittest
from datetime import datetime
import sqlite3

# Add the backend source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chatbot_backend', 'src'))

# Import chatbot components
from services.nlp_engine import NLPEngine

class ChatbotTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.nlp_engine = NLPEngine()
        self.test_results = {
            'nlp_tests': [],
            'api_tests': [],
            'performance_tests': [],
            'integration_tests': [],
            'summary': {}
        }
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Chatbot Testing")
        print("=" * 60)
        
        # Test NLP Engine
        self.test_nlp_functionality()
        
        # Test API Endpoints
        self.test_api_endpoints()
        
        # Test Performance
        self.test_performance()
        
        # Test Integration
        self.test_integration()
        
        # Generate Summary
        self.generate_test_summary()
        
        # Save Results
        self.save_test_results()
        
        return self.test_results
    
    def test_nlp_functionality(self):
        """Test Natural Language Processing capabilities"""
        print("\n📝 Testing NLP Engine Functionality")
        print("-" * 40)
        
        test_cases = [
            {
                'input': 'Hello, how can you help me?',
                'expected_intent': 'greeting',
                'description': 'Basic greeting recognition'
            },
            {
                'input': 'Create a task to finish the project report',
                'expected_intent': 'task_creation',
                'description': 'Task creation intent'
            },
            {
                'input': 'Schedule a meeting with John tomorrow at 2 PM',
                'expected_intent': 'schedule_meeting',
                'description': 'Meeting scheduling intent'
            },
            {
                'input': 'Remind me to call the client',
                'expected_intent': 'reminder',
                'description': 'Reminder setting intent'
            },
            {
                'input': 'Give me some productivity tips',
                'expected_intent': 'productivity_tips',
                'description': 'Productivity advice request'
            },
            {
                'input': 'What time is it?',
                'expected_intent': 'time_management',
                'description': 'Time-related query'
            },
            {
                'input': 'What can you do for me?',
                'expected_intent': 'help',
                'description': 'Help request'
            },
            {
                'input': 'Goodbye',
                'expected_intent': 'goodbye',
                'description': 'Farewell recognition'
            },
            {
                'input': 'asdfghjkl random text',
                'expected_intent': 'unknown',
                'description': 'Unknown intent handling'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = self.nlp_engine.process_message(test_case['input'])
                
                # Check intent classification
                intent_correct = result['intent'] == test_case['expected_intent']
                confidence = result['confidence']
                
                test_result = {
                    'test_id': f'NLP_{i:02d}',
                    'description': test_case['description'],
                    'input': test_case['input'],
                    'expected_intent': test_case['expected_intent'],
                    'actual_intent': result['intent'],
                    'confidence': confidence,
                    'intent_correct': intent_correct,
                    'response_generated': bool(result['response']),
                    'entities_extracted': len(result['entities']) > 0,
                    'sentiment_analyzed': 'sentiment' in result,
                    'status': 'PASS' if intent_correct and confidence > 0.1 else 'FAIL'
                }
                
                self.test_results['nlp_tests'].append(test_result)
                
                status_icon = "✅" if test_result['status'] == 'PASS' else "❌"
                print(f"{status_icon} {test_result['test_id']}: {test_result['description']}")
                print(f"   Input: '{test_case['input']}'")
                print(f"   Expected: {test_case['expected_intent']}, Got: {result['intent']} ({confidence:.2f})")
                
            except Exception as e:
                test_result = {
                    'test_id': f'NLP_{i:02d}',
                    'description': test_case['description'],
                    'error': str(e),
                    'status': 'ERROR'
                }
                self.test_results['nlp_tests'].append(test_result)
                print(f"❌ {test_result['test_id']}: ERROR - {str(e)}")
    
    def test_api_endpoints(self):
        """Test REST API endpoints"""
        print("\n🌐 Testing API Endpoints")
        print("-" * 40)
        
        api_tests = [
            {
                'name': 'Chat Endpoint - POST /api/chat',
                'method': 'POST',
                'url': '/api/chat',
                'data': {
                    'message': 'Hello, test message',
                    'session_id': 'test_session_123',
                    'user_id': 1
                },
                'expected_status': 200
            },
            {
                'name': 'Get Conversations - GET /api/conversations',
                'method': 'GET',
                'url': '/api/conversations?user_id=1',
                'expected_status': 200
            },
            {
                'name': 'Get Intents - GET /api/intents',
                'method': 'GET',
                'url': '/api/intents',
                'expected_status': 200
            },
            {
                'name': 'Get Analytics - GET /api/analytics',
                'method': 'GET',
                'url': '/api/analytics?user_id=1',
                'expected_status': 200
            }
        ]
        
        for i, test in enumerate(api_tests, 1):
            try:
                url = self.base_url + test['url']
                
                if test['method'] == 'POST':
                    response = requests.post(
                        url, 
                        json=test['data'],
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                else:
                    response = requests.get(url, timeout=10)
                
                # Analyze response
                status_correct = response.status_code == test['expected_status']
                response_time = response.elapsed.total_seconds()
                
                try:
                    response_data = response.json()
                    valid_json = True
                except:
                    response_data = None
                    valid_json = False
                
                test_result = {
                    'test_id': f'API_{i:02d}',
                    'name': test['name'],
                    'method': test['method'],
                    'url': test['url'],
                    'expected_status': test['expected_status'],
                    'actual_status': response.status_code,
                    'response_time': response_time,
                    'valid_json': valid_json,
                    'status_correct': status_correct,
                    'status': 'PASS' if status_correct and valid_json else 'FAIL'
                }
                
                self.test_results['api_tests'].append(test_result)
                
                status_icon = "✅" if test_result['status'] == 'PASS' else "❌"
                print(f"{status_icon} {test_result['test_id']}: {test['name']}")
                print(f"   Status: {response.status_code} (Expected: {test['expected_status']})")
                print(f"   Response Time: {response_time:.3f}s")
                
            except requests.exceptions.RequestException as e:
                test_result = {
                    'test_id': f'API_{i:02d}',
                    'name': test['name'],
                    'error': str(e),
                    'status': 'ERROR'
                }
                self.test_results['api_tests'].append(test_result)
                print(f"❌ {test_result['test_id']}: ERROR - {str(e)}")
    
    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ Testing Performance Metrics")
        print("-" * 40)
        
        # Test NLP processing speed
        test_messages = [
            "Hello, how are you?",
            "Create a task to review the quarterly report by Friday",
            "Schedule a meeting with the development team next Tuesday at 3 PM",
            "Give me some productivity tips for better time management"
        ]
        
        nlp_times = []
        for message in test_messages:
            start_time = time.time()
            result = self.nlp_engine.process_message(message)
            end_time = time.time()
            processing_time = end_time - start_time
            nlp_times.append(processing_time)
        
        avg_nlp_time = sum(nlp_times) / len(nlp_times)
        max_nlp_time = max(nlp_times)
        
        # Test API response times
        api_times = []
        for _ in range(5):
            try:
                start_time = time.time()
                response = requests.post(
                    f'{self.base_url}/api/chat',
                    json={
                        'message': 'Performance test message',
                        'session_id': f'perf_test_{int(time.time())}',
                        'user_id': 1
                    },
                    timeout=10
                )
                end_time = time.time()
                if response.status_code == 200:
                    api_times.append(end_time - start_time)
            except:
                pass
        
        avg_api_time = sum(api_times) / len(api_times) if api_times else 0
        
        performance_result = {
            'nlp_processing': {
                'average_time': avg_nlp_time,
                'max_time': max_nlp_time,
                'samples': len(nlp_times),
                'meets_requirement': avg_nlp_time < 1.0  # < 1 second requirement
            },
            'api_response': {
                'average_time': avg_api_time,
                'samples': len(api_times),
                'meets_requirement': avg_api_time < 2.0  # < 2 seconds requirement
            }
        }
        
        self.test_results['performance_tests'].append(performance_result)
        
        print(f"📊 NLP Processing Performance:")
        print(f"   Average Time: {avg_nlp_time:.3f}s")
        print(f"   Max Time: {max_nlp_time:.3f}s")
        print(f"   Meets Requirement (<1s): {'✅' if performance_result['nlp_processing']['meets_requirement'] else '❌'}")
        
        print(f"📊 API Response Performance:")
        print(f"   Average Time: {avg_api_time:.3f}s")
        print(f"   Samples: {len(api_times)}")
        print(f"   Meets Requirement (<2s): {'✅' if performance_result['api_response']['meets_requirement'] else '❌'}")
    
    def test_integration(self):
        """Test end-to-end integration"""
        print("\n🔗 Testing Integration Scenarios")
        print("-" * 40)
        
        integration_scenarios = [
            {
                'name': 'Complete Conversation Flow',
                'messages': [
                    'Hello',
                    'Create a task to prepare presentation',
                    'Schedule a meeting tomorrow at 10 AM',
                    'Give me productivity tips',
                    'Goodbye'
                ]
            }
        ]
        
        for scenario in integration_scenarios:
            session_id = f'integration_test_{int(time.time())}'
            scenario_results = []
            
            for i, message in enumerate(scenario['messages'], 1):
                try:
                    response = requests.post(
                        f'{self.base_url}/api/chat',
                        json={
                            'message': message,
                            'session_id': session_id,
                            'user_id': 1
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        scenario_results.append({
                            'step': i,
                            'message': message,
                            'response': data.get('bot_response', ''),
                            'intent': data.get('intent', ''),
                            'confidence': data.get('confidence', 0),
                            'success': True
                        })
                    else:
                        scenario_results.append({
                            'step': i,
                            'message': message,
                            'error': f'HTTP {response.status_code}',
                            'success': False
                        })
                        
                except Exception as e:
                    scenario_results.append({
                        'step': i,
                        'message': message,
                        'error': str(e),
                        'success': False
                    })
            
            success_rate = sum(1 for r in scenario_results if r['success']) / len(scenario_results)
            
            integration_result = {
                'scenario_name': scenario['name'],
                'session_id': session_id,
                'steps': scenario_results,
                'success_rate': success_rate,
                'status': 'PASS' if success_rate >= 0.8 else 'FAIL'
            }
            
            self.test_results['integration_tests'].append(integration_result)
            
            status_icon = "✅" if integration_result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {scenario['name']}")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Steps Completed: {sum(1 for r in scenario_results if r['success'])}/{len(scenario_results)}")
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n📋 Test Summary")
        print("=" * 60)
        
        # NLP Tests Summary
        nlp_passed = sum(1 for t in self.test_results['nlp_tests'] if t.get('status') == 'PASS')
        nlp_total = len(self.test_results['nlp_tests'])
        
        # API Tests Summary
        api_passed = sum(1 for t in self.test_results['api_tests'] if t.get('status') == 'PASS')
        api_total = len(self.test_results['api_tests'])
        
        # Integration Tests Summary
        integration_passed = sum(1 for t in self.test_results['integration_tests'] if t.get('status') == 'PASS')
        integration_total = len(self.test_results['integration_tests'])
        
        # Performance Summary
        performance_data = self.test_results['performance_tests'][0] if self.test_results['performance_tests'] else {}
        nlp_performance_ok = performance_data.get('nlp_processing', {}).get('meets_requirement', False)
        api_performance_ok = performance_data.get('api_response', {}).get('meets_requirement', False)
        
        summary = {
            'nlp_tests': {
                'passed': nlp_passed,
                'total': nlp_total,
                'success_rate': nlp_passed / nlp_total if nlp_total > 0 else 0
            },
            'api_tests': {
                'passed': api_passed,
                'total': api_total,
                'success_rate': api_passed / api_total if api_total > 0 else 0
            },
            'integration_tests': {
                'passed': integration_passed,
                'total': integration_total,
                'success_rate': integration_passed / integration_total if integration_total > 0 else 0
            },
            'performance': {
                'nlp_performance_ok': nlp_performance_ok,
                'api_performance_ok': api_performance_ok
            },
            'overall_status': 'PASS' if all([
                nlp_passed / nlp_total >= 0.8 if nlp_total > 0 else True,
                api_passed / api_total >= 0.8 if api_total > 0 else True,
                integration_passed / integration_total >= 0.8 if integration_total > 0 else True,
                nlp_performance_ok,
                api_performance_ok
            ]) else 'FAIL'
        }
        
        self.test_results['summary'] = summary
        
        print(f"🧠 NLP Tests: {nlp_passed}/{nlp_total} passed ({summary['nlp_tests']['success_rate']:.1%})")
        print(f"🌐 API Tests: {api_passed}/{api_total} passed ({summary['api_tests']['success_rate']:.1%})")
        print(f"🔗 Integration Tests: {integration_passed}/{integration_total} passed ({summary['integration_tests']['success_rate']:.1%})")
        print(f"⚡ Performance: NLP {'✅' if nlp_performance_ok else '❌'}, API {'✅' if api_performance_ok else '❌'}")
        print(f"\n🎯 Overall Status: {summary['overall_status']}")
        
        return summary
    
    def save_test_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/ubuntu/chatbot_project/test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: {filename}")
        return filename

def main():
    """Main testing function"""
    print("🤖 Intelligent Text-Based Chatbot - Comprehensive Testing Suite")
    print("=" * 70)
    
    # Initialize tester
    tester = ChatbotTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print final status
    overall_status = results['summary']['overall_status']
    status_icon = "🎉" if overall_status == 'PASS' else "⚠️"
    
    print(f"\n{status_icon} Testing Complete - Overall Status: {overall_status}")
    
    return results

if __name__ == "__main__":
    main()

