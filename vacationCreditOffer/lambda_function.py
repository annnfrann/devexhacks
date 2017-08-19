"""

"""

from __future__ import print_function


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    The context parameter is from the AWS Lambda service (e.g. time remain before
    timeout, CloudWatch logging info, AWS requestID sent to client, etc.)
    """
    # Logging
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AddDestination":
        return set_destination(intent, session)
    elif intent_name == "LearnMore":
        return learn_more(intent, session)
    elif intent_name == "ApplyForCredit":
        return apply(intent, session)
    elif intent_name == "GetPrequalified":
        return get_prequalified(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    # To initialize the session to have some attributes, add those here
    session_attributes = {}

    card_title = "Welcome"
    speech_output = "Where are you looking to go. " \
                    "Please tell me by saying a location. "
    reprompt_text = "Please tell me where you want to go?. "
    should_end_session = False

    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session)


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying ... "
    should_end_session = True
    return build_alexa_response({}, card_title, speech_output, None, should_end_session)


def set_destination(intent, session):
    """ Sets the destination
    """

    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    destination = ''
    if intent['slots']['US_cities'].get('value'):
        destination = intent['slots']['US_cities']['value']

    if intent['slots']['countries'].get('value'):
        destination = intent['slots']['countries']['value']

    if destination:
        session_attributes = {'destination': destination}

        # TODO get best CC
        speech_output = " Based on flight information to " + destination + \
                        ". you may qualify for a Capital one card. " \
                        "Would you like to apply or proceed with booking?"
        reprompt_text = "Would you like to apply or proceed with booking?"
    else:
        speech_output = "I'm not sure where you want to go. " \
                        "Please try again."
        reprompt_text = "You can tell me your destination by saying, " \
                        "I want to go to New Zealand."
    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session)


def get_prequalified(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    # set     session_attributes = {}
   
    speech_output = "Would you like to hear your pre qualified offers or proceed with booking?,"
    reprompt_text = "Would you like to hear your pre qualified offers or proceed with booking?"
    
    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session)


def hear_offer(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    # If prequailified 
    
    speech_output = "Great news cool stuff here from capital one. CHeck your email"
    reprompt_text = "Mic drop."

    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session)


# --------------- Helpers that build all of the responses ----------------------

def build_alexa_response(session_attributes, title, output, reprompt_text, should_end_session):
    speechlet_response = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
