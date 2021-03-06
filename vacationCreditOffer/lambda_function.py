"""

"""

from __future__ import print_function
import requests
import json


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
        event['session']['attributes'] = {}
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

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
    elif intent_name == "Apply":
        return apply(intent, session)
    elif intent_name == "GetSocial":
        return get_prequalified(intent, session)
    elif intent_name == "FindOutMore":
        return tell_me_more(intent, session)
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
    content = '... planning a vacation...'
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'
    speech_output = "Where do you want to go?."
    reprompt_text = "Please tell me where you want to go?. "
    should_end_session = False

    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session, content, image_url)


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying ... "
    should_end_session = True
    content = 'end'
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'
    return build_alexa_response({}, card_title, speech_output, None, should_end_session, content, image_url)


def set_destination(intent, session):
    """ Sets the destination
    """

    card_title = intent['name']

    if session.get('attributes'):
        session_attributes = session['attributes']
    else:
        session_attributes = {}

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

    content = destination
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'
    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session, content, image_url)


def apply(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    speech_output = "Please give me your tax id number,"
    reprompt_text = "I need your tax id numbner to continue."

    content = 'reaching out to CapitalOne...'
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'

    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session, content, image_url)


# User give SSN
def get_prequalified(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False

    session_attributes = {}
    session_attributes.update({'ssn': 888888888})
    session_attributes.update({'name': 'Matt'})

    # if prequalify
    token = co_getToken()
    data = dict(firstName=session_attributes['name'], taxId=str(session_attributes['ssn']))
    answer = co_getPreQualify(token, data)
    # If prequailified

    speech_output = "Sorry, you are not prequalified"
    content = 'Sorry'
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'
    if answer.json()['isPrequalified']:
        pname = answer.json()['products'][0]['productName']
        terms = answer.json()['products'][0]['terms']['purchaseAprTerms'].rstrip()
        benefit = answer.json()['products'][0]['terms']['primaryBenefit'].rstrip()
        session['benefits'] = benefit
        pname = pname[0:pname.find('<')]
        speech_output = 'Congratulations you are prequalified for the following card: '
        speech_output += pname + ' that has ' + terms

        content = 'QuicksilverOne From Capital One'
        image_url = 'https://thepointsguy.com/wp-content/uploads/2017/05/quicksilver-redesign5b25d5b15d.jpg'

    reprompt_text = None


    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session, content, image_url)

def tell_me_more(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = True

    speech_output = 'With this card you can earn unlimited 1.5% cash back on every purchase, every day'
    speech_output +=  '. An email will be sent with the application details. Enjoy your trip'
    reprompt_text = None

    content = '1.5% Cash Back on Every Purchase'
    image_url = 'https://s3.amazonaws.com/capitalexaphoto/IMG_20170819_143730+(1).jpg'

    return build_alexa_response(session_attributes, card_title, speech_output,
                                reprompt_text, should_end_session, content, image_url)

# --------------- Helpers that build all of the responses ----------------------

def build_alexa_response(session_attributes, title, output, reprompt_text, should_end_session, content, image_url):
    speechlet_response = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': content,
            'image': {
                'smallImageUrl': image_url
            }
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


def co_getToken():
    url = 'https://api.devexhacks.com/oauth2/token'
    data = dict(client_id='vgw3sf4f8nq3b98i1gdfr8wpx4gpty0ska52',client_secret='eb5f6rda6v0d1ld8y4fymkudo86gorrc47cj')
    data['grant_type']='client_credentials'
    r = requests.post(url,data = data)
    return r.json()['access_token']

def co_getPreQualify(token,data):
    url = 'http://api.devexhacks.com/credit-offers/prequalifications'
    header = dict(Authorization= 'Bearer '+token)
    header['Content-Type'] = 'application/json;v=3'
    r = requests.post(url,json=data,headers=header)
    return r
