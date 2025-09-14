import uuid

from financial_agent.dataclass import UserDetails


class ResponseService:
    def __init__(self, user_details: UserDetails, session_id: str = None):
        self.user_details = user_details
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

    def base_page(self):
        return {
            "data": {
                "title": {
                    "alignment": "top-center",
                    "list": [
                        {
                            "title": {
                                "text": f"Welcome {self.user_details.first_name}!",
                                "color": "#191C1F",
                                "font": "h2headline"
                            },
                            "type": "text"
                        }
                    ]
                },
                "subtitle": {
                    "alignment": "top-center",
                    "list": [
                        {
                            "title": {
                                "text": "I am here to understand your investments, share insights, make your investments plan and suggest steps to grow your money and reach your goals",
                                "color": "#757779",
                                "font": "body"
                            },
                            "type": "text"
                        }
                    ]
                },
                "chips": {
                    "api_key": "annual_income",
                    "chips_item": [
                        {
                            "selected_appearance": {
                                "bgColor": "#017AFF",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Understand Investment Performance",
                                    "color": "#FFFFFF",
                                    "font": "Body1"
                                }
                            },
                            "unselected_appearance": {
                                "bgColor": "#E8F4FD",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Understand Investment Performance",
                                    "color": "#017AFF",
                                    "font": "Body1"
                                }
                            },
                            "cta": {
                                "primary": {
                                    "request": {
                                        "method": "POST",
                                        "body": {
                                            "session_id": "{{session_id}}",
                                            "query": "i want to buy a house in next 5 years?"
                                        },
                                        "endpoint": ""
                                    },
                                    "type": "chatbot-cta"
                                }
                            },
                            "api_value": "Monthly"
                        },
                        {
                            "selected_appearance": {
                                "bgColor": "#017AFF",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Start New Investment",
                                    "color": "#FFFFFF",
                                    "font": "Body1"
                                }
                            },
                            "unselected_appearance": {
                                "bgColor": "#E8F4FD",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Start New Investment",
                                    "color": "#017AFF",
                                    "font": "Body1"
                                }
                            },
                            "cta": {
                                "primary": {
                                    "request": {
                                        "method": "POST",
                                        "body": {
                                            "prompt": ""
                                        },
                                        "endpoint": "https://jsonblob.com/api/1331863681109254144"
                                    },
                                    "type": "chatbot-cta"
                                }
                            },
                            "api_value": "Quaterly"
                        },
                        {
                            "selected_appearance": {
                                "bgColor": "#017AFF",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Plan my investments",
                                    "color": "#FFFFFF",
                                    "font": "Body1"
                                }
                            },
                            "unselected_appearance": {
                                "bgColor": "#E8F4FD",
                                "border_color": "#017AFF",
                                "radius": 54,
                                "title": {
                                    "text": "Plan my investments",
                                    "color": "#017AFF",
                                    "font": "Body1"
                                }
                            },
                            "cta": {
                                "primary": {
                                    "request": {
                                        "method": "POST",
                                        "body": {
                                            "prompt": ""
                                        },
                                        "endpoint": "https://jsonblob.com/api/1331863681109254144"
                                    },
                                    "type": "chatbot-cta"
                                }
                            },
                            "api_value": "Half yearly"
                        }
                    ]
                },
                "page_event_name": "",
                "page_event_props": {}
            }
        }

    def query_response(self, message: str):
        return {
            "title1": {
                "alignment": "top-left",
                "list": [
                    {
                        "title": {
                            "text": message,
                            "color": "#191C1F",
                            "font": "subtitle2"
                        },
                        "type": "text"
                    }
                ]
            }
        }
