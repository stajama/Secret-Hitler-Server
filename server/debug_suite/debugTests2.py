#!/usr/bin/python3

from ClientObject import TestPlayer

import requests
import json
import time

def testGame1():
    """5 player test game, responding solely to Http/Json information from server."""

    ###### LOCAL HELPERS ######
    def statusInfoCheck5player1(currentID, currentMessage, libCount=None, fasCount=None):
        check = a.client_call_for_json(f'client/client_status/{a.ids}')
        if check['name'] != 'a' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check) + "\n" + currentMessage)
        check = b.client_call_for_json(f'client/client_status/{b.ids}')
        if check['name'] != 'b' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = c.client_call_for_json(f'client/client_status/{c.ids}')
        if check['name'] != 'c' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = d.client_call_for_json(f'client/client_status/{d.ids}')
        if check['name'] != 'd' or check['party'] != 'Fascist' or check['role'] != 'Fascist' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Hitler'] != 'e' or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        check = e.client_call_for_json(f'client/client_status/{e.ids}')
        if check['name'] != 'e' or check['party'] != 'Fascist' or check['role'] != 'Hitler' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        if libCount != None:
            if check["libPolicies"] != libCount:
                raise AssertionError("something wrong in status, too few liberal policies on count")
        if fasCount != None:
            if check["fasPolicies"] != fasCount:
                raise AssertionError("something wrong in status, too few fascist policies on count")            
        return 'done'

    ####### THE MEAT & POTATOES ##########
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    check = a.client_call_for_http('setup/1/5')
    if check != 'confirm':
        raise AssertionError('setup Error: ' + check)

    waitForIt()
    a.ids = a.client_call_for_http(f'client/join_game/{a.name}')
    a.id = int(a.ids)
    waitForIt()
    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    waitForIt()
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    waitForIt()
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    waitForIt()
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)
    waitForIt()

    x = TestPlayer('frank')
    check = x.client_call_for_http(f'client/join_game/{x.name}')
    if "Unable to join, game is full." != check:
        raise AssertionError("frank wasn't supposed to be able to join." + x.text)

    waitForIt()

    x = input('''HOLDING: run /shs/server/quickDebug.py - mockData1()\n
        Enter to confirm.''')
    waitForIt()
    try:
        statusInfoCheck5player1(3, "The current President is a. Waiting for the President to nominate a Chancellor.")
    except AssertionError as theProblem:
        raise theProblem
    waitForIt()

    ###########START OF GAME LOOP##################
    # turn 1: a is president, a elections b, all vote ya, a gives b 1 lib/1 fas, b choses the lib. All is well.
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    others = [b, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = a.client_call_for_http(f'client/nominate_chancellor_order/{a.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{a.name} nominated {b.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/president_play/{a.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {b.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections c, all vote ya, b gives c 1 lib/1 fas, c choses the lib. All is well.
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    others = [a, c, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if a.ids in check:
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{b.name} nominated {c.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/president_play/{b.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {c.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 3: c is president, c elections d, all vote ya, c gives d 1 lib/1 fas, d choses the lib. All is well.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    others = [a, b, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if b.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.", libCount=2)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/president_play/{c.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/chancellor_play/{d.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')

    ###########START OF GAME LOOP##################
    # turn 4: d is president, d elections e, all vote ya, d gives e 1 lib/1 fas, e choses the lib. All is well.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [a, b, c, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if c.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{e.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {e.name} for Chancellor.", libCount=3)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {e.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {d.name} and Chancellor {e.name} will now enact a policy decision.")

    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/president_play/{d.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = e.client_call_for_http(f'client/chancellor_play/{e.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {e.name}. Waiting for the President to nominate a Chancellor.')

    ###########START OF GAME LOOP##################
    # turn 5: e is president, e elections a, all vote ya, e gives a 1 lib/1 fas, a choses the lib. Liberals win.
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    others = [a, c, b, d]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if d.ids in check: # d is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = e.client_call_for_http(f'client/nominate_chancellor_order/{e.ids}/{a.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{e.name} nominated {a.name} for Chancellor.", libCount=4)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = e.client_call_for_http(f'client/president_play/{e.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/chancellor_play/{a.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    waitForIt()
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    waitForIt()
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    waitForIt()
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    waitForIt()
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    statusInfoCheck5player1(100, "The Liberals have achieved a policy victory.", libCount=5)
    waitForIt()
    for playerPlayer in [a, b, c, d, e]:
        check = playerPlayer.client_call_for_json('client/game_over')
        if check != {'a': 'a : Liberal : Alive',
                     'b': 'b : Liberal : Alive',
                     'c': 'c : Liberal : Alive',
                     'd': 'd : Fascist : Alive',
                     'e': 'e : Hitler : Alive',
                     'fasPolicyCount': 0,
                     'libPolicyCount': 5,
                     'whatHappened': "The Liberals have achieved a policy victory."}:
            raise AssertionError('something wrong with end results page: ' + str(check))

    print('done')

def testGame2():
    """5 player test game, responding solely to Http/Json information from server. Players elect Hitler after 3 fascist policies have been enacted."""

    ###### LOCAL HELPERS ######
    def statusInfoCheck5player1(currentID, currentMessage, libCount=None, fasCount=None):
        check = a.client_call_for_json(f'client/client_status/{a.ids}')
        if check['name'] != 'a' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check) + "\n" + currentMessage)
        check = b.client_call_for_json(f'client/client_status/{b.ids}')
        if check['name'] != 'b' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = c.client_call_for_json(f'client/client_status/{c.ids}')
        if check['name'] != 'c' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = d.client_call_for_json(f'client/client_status/{d.ids}')
        if check['name'] != 'd' or check['party'] != 'Fascist' or check['role'] != 'Fascist' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Hitler'] != 'e' or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        check = e.client_call_for_json(f'client/client_status/{e.ids}')
        if check['name'] != 'e' or check['party'] != 'Fascist' or check['role'] != 'Hitler' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        if libCount != None:
            if check["libPolicies"] != libCount:
                raise AssertionError("something wrong in status, too few liberal policies on count")
        if fasCount != None:
            if check["fasPolicies"] != fasCount:
                raise AssertionError("something wrong in status, too few fascist policies on count")            
        return 'done'

    ####### THE MEAT & POTATOES ##########
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    check = a.client_call_for_http('setup/1/5')
    if check != 'confirm':
        raise AssertionError('setup Error')

    waitForIt()
    a.ids = a.client_call_for_http(f'client/join_game/{a.name}')
    a.id = int(a.ids)
    waitForIt()
    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    waitForIt()
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    waitForIt()
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    waitForIt()
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)
    waitForIt()

    x = TestPlayer('frank')
    check = x.client_call_for_http(f'client/join_game/{x.name}')
    if "Unable to join, game is full." != check:
        raise AssertionError("frank wasn't supposed to be able to join." + x.text)

    waitForIt()

    x = input('''HOLDING: run /shs/server/quickDebug.py - mockData1()\n
        Enter to confirm.''')
    waitForIt()
    try:
        statusInfoCheck5player1(3, "The current President is a. Waiting for the President to nominate a Chancellor.")
    except AssertionError as theProblem:
        raise theProblem
    waitForIt()

    ###########START OF GAME LOOP##################
    # turn 1: a is president, a elections b, all vote ya, a gives b 1 lib/1 fas, b choses the fascist. 1 bad policy.
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    others = [b, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = a.client_call_for_http(f'client/nominate_chancellor_order/{a.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{a.name} nominated {b.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/president_play/{a.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {b.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections c, all vote ya, b gives c 1 lib/1 fas, c choses the fas. 2 bad policies.
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    others = [a, c, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if a.ids in check:
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{b.name} nominated {c.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.", fasCount=1, libCount=0)

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/president_play/{b.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {c.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 3: c is president, c elections d, all vote ya, c gives d 1 lib/1 fas, d choses the fas. c gets to policy peek.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    others = [a, b, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if b.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.", libCount=0, fasCount=2)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/president_play/{c.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/chancellor_play/{d.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt')
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt')
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt')
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(16, "The President will now look at the top 3 policy cards in the Policy Deck.", fasCount=3, libCount=0)

    checkAgainst = {'information': "The President will now look at the top 3 policy cards in the Policy Deck."}
    waitForIt()
    if a.client_call_for_json(f'client/president_policy_peek/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_policy_peek/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = c.client_call_for_json(f'client/president_policy_peek/{c.ids}')
        if len(check) != 4 or not (check['1'] != "Liberal" or check['1'] != "Fascist") or not (check['2'] != "Liberal" or check['2'] != "Fascist") or not (check['3'] != "Liberal" or check['3'] != "Fascist") or check['information'] != "You may now peek at the next three policy cards in the policy deck.":
            raise AssertionError('policy peek not working, ' + str(check))
    except KeyError:
        raise AssertionError('not all cards present in president policy peek' + str(check))
    waitForIt()
    if d.client_call_for_json(f'client/president_policy_peek/{d.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_json(f'client/president_policy_peek/{e.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = c.client_call_for_http(f'client/president_policy_peek_confirm/{c.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)


    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')

    ###########START OF GAME LOOP##################
    # turn 4: d is president, d elections e, all vote ya, e is Hilter and 3 fascists policies have been enacted. Game over.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [a, b, c, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if c.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{e.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {e.name} for Chancellor.", fasCount=3)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {e.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(100, f"The Fascists have achieved victory by getting Hitler elected Chancellor.", fasCount=3)

    check = a.client_call_for_json('client/game_over')
    checkAgainst = {'a': 'a : Liberal : Alive',
                    'b': 'b : Liberal : Alive',
                    'c': 'c : Liberal : Alive',
                    'd': 'd : Fascist : Alive',
                    'e': 'e : Hitler : Alive',
                    'fasPolicyCount': 3,
                    'libPolicyCount': 0,
                    'whatHappened': "The Fascists have achieved victory by getting Hitler elected Chancellor."}
    if checkAgainst != check:
        raise AssertionError('end game text wrong: ' + str(check))
    print('done')

def testGame3():
    """5 player test game, responding solely to Http/Json information from server. Testing executive powers."""

    ###### LOCAL HELPERS ######
    def statusInfoCheck5player1(currentID, currentMessage, libCount=None, fasCount=None):
        check = a.client_call_for_json(f'client/client_status/{a.ids}')
        if check['name'] != 'a' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check) + "\n" + currentMessage)
        check = b.client_call_for_json(f'client/client_status/{b.ids}')
        if check['name'] != 'b' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = c.client_call_for_json(f'client/client_status/{c.ids}')
        if check['name'] != 'c' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = d.client_call_for_json(f'client/client_status/{d.ids}')
        if check['name'] != 'd' or check['party'] != 'Fascist' or check['role'] != 'Fascist' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Hitler'] != 'e' or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        check = e.client_call_for_json(f'client/client_status/{e.ids}')
        try:
            if check['name'] != 'e' or check['party'] != 'Fascist' or check['role'] != 'Hitler' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Other Fascists'] != "d":
                raise AssertionError("something wrong with get_status()" + str(check))
        except KeyError:
            raise KeyError('huh? :' + str(check))
        if libCount != None:
            if check["libPolicies"] != libCount:
                raise AssertionError("something wrong in status, too few liberal policies on count")
        if fasCount != None:
            if check["fasPolicies"] != fasCount:
                raise AssertionError("something wrong in status, too few fascist policies on count")            
        return 'done'

    ####### THE MEAT & POTATOES ##########
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    check = a.client_call_for_http('setup/1/5')
    if check != 'confirm':
        raise AssertionError('setup Error: ' + str(check))

    waitForIt()
    a.ids = a.client_call_for_http(f'client/join_game/{a.name}')
    a.id = int(a.ids)
    waitForIt()
    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    waitForIt()
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    waitForIt()
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    waitForIt()
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)
    waitForIt()

    x = TestPlayer('frank')
    check = x.client_call_for_http(f'client/join_game/{x.name}')
    if "Unable to join, game is full." != check:
        raise AssertionError("frank wasn't supposed to be able to join." + x.text)

    waitForIt()

    x = input('''HOLDING: run /shs/server/quickDebug.py - mockData1()\n
        Enter to confirm.''')
    waitForIt()
    try:
        statusInfoCheck5player1(3, "The current President is a. Waiting for the President to nominate a Chancellor.")
    except AssertionError as theProblem:
        raise theProblem
    waitForIt()

    ###########START OF GAME LOOP##################
    # turn 1: a is president, a elections b, all vote ya, a gives b 1 lib/1 fas, b choses the fascist. 1 bad policy.
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    others = [b, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = a.client_call_for_http(f'client/nominate_chancellor_order/{a.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{a.name} nominated {b.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/president_play/{a.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {b.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections c, all vote ya, b gives c 1 lib/1 fas, c choses the fas. 2 bad policies.
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    others = [a, c, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if a.ids in check:
        # raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{b.name} nominated {c.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.", fasCount=1, libCount=0)

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/president_play/{b.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {c.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 3: c is president, c elections d, all vote ya, c gives d 1 lib/1 fas, d choses the fas. c gets to policy peek.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    others = [a, b, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if b.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.", libCount=0, fasCount=2)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/president_play/{c.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/chancellor_play/{d.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt')
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt')
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt')
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(16, "The President will now look at the top 3 policy cards in the Policy Deck.", fasCount=3, libCount=0)

    checkAgainst = {'information': "The President will now look at the top 3 policy cards in the Policy Deck."}
    waitForIt()
    if a.client_call_for_json(f'client/president_policy_peek/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_policy_peek/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = c.client_call_for_json(f'client/president_policy_peek/{c.ids}')
        if len(check) != 4 or not (check['1'] != "Liberal" or check['1'] != "Fascist") or not (check['2'] != "Liberal" or check['2'] != "Fascist") or not (check['3'] != "Liberal" or check['3'] != "Fascist") or check['information'] != "You may now peek at the next three policy cards in the policy deck.":
            raise AssertionError('policy peek not working, ' + str(check))
    except KeyError:
        raise AssertionError('not all cards present in president policy peek' + str(check))
    waitForIt()
    if d.client_call_for_json(f'client/president_policy_peek/{d.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_json(f'client/president_policy_peek/{e.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = c.client_call_for_http(f'client/president_policy_peek_confirm/{c.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)


    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')

    ###########START OF GAME LOOP##################
    # turn 4: d is president, d elections a, all vote ya, d gives a 1 lib/1 fas, a choses the fas. d gets execution power 1, shoots e, game over.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [a, b, c, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if c.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{a.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {a.name} for Chancellor.", libCount=0, fasCount=3)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {d.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/president_play/{d.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/chancellor_play/{a.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt')
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt')
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt')
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(17, "The President must now select a player to execute.", fasCount=4, libCount=0)

    checkAgainst = {'information': "The President must now select a player to execute."}
    waitForIt()
    if a.client_call_for_json(f'client/president_execute/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_execute/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = d.client_call_for_json(f'client/president_execute/{d.ids}')
        if check != {'information': "You must now execute a player.",
                     a.ids: a.name,
                     b.ids: b.name,
                     c.ids: c.name,
                     e.ids: e.name}:
            raise AssertionError('execution selection page not working, ' + str(check))
    except KeyError:
        raise AssertionError('eligible list likely wrong' + str(check))
    waitForIt()
    if c.client_call_for_json(f'client/president_execute/{c.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_json(f'client/president_execute/{e.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = d.client_call_for_http(f'client/president_execute_order/{d.ids}/{e.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)


    waitForIt()
    statusInfoCheck5player1(100, f'The Liberals have achieved victory by assassinating Hitler.')

    check = a.client_call_for_json('client/game_over')
    checkAgainst = {'a': 'a : Liberal : Alive',
                    'b': 'b : Liberal : Alive',
                    'c': 'c : Liberal : Alive',
                    'd': 'd : Fascist : Alive',
                    'e': 'e : Hitler : Dead',
                    'fasPolicyCount': 4,
                    'libPolicyCount': 0,
                    'whatHappened': "The Liberals have achieved victory by assassinating Hitler."}
    if checkAgainst != check:
        raise AssertionError('end game text wrong: ' + str(check))
    print('done')

def testGame4():
    """5 player test game, responding solely to Http/Json information from server. Testing all executive powers and fascist policy win."""

    ###### LOCAL HELPERS ######
    def statusInfoCheck5player1(currentID, currentMessage, libCount=None, fasCount=None, eTrack=None):
        check = a.client_call_for_json(f'client/client_status/{a.ids}')
        if check['name'] != 'a' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check) + "\n" + currentMessage)
        check = b.client_call_for_json(f'client/client_status/{b.ids}')
        if check['name'] != 'b' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = c.client_call_for_json(f'client/client_status/{c.ids}')
        if check['name'] != 'c' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = d.client_call_for_json(f'client/client_status/{d.ids}')
        if check['name'] != 'd' or check['party'] != 'Fascist' or check['role'] != 'Fascist' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Hitler'] != 'e' or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        check = e.client_call_for_json(f'client/client_status/{e.ids}')
        try:
            if check['name'] != 'e' or check['party'] != 'Fascist' or check['role'] != 'Hitler' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Other Fascists'] != "d":
                raise AssertionError("something wrong with get_status()" + str(check))
        except KeyError:
            raise KeyError('huh? :' + str(check))
        if libCount != None:
            if check["libPolicies"] != libCount:
                raise AssertionError("something wrong in status, too few liberal policies on count")
        if fasCount != None:
            if check["fasPolicies"] != fasCount:
                raise AssertionError("something wrong in status, too few fascist policies on count")  
        if eTrack != None:
            if check['electionTracker'] != eTrack:
                print(check['electionTracker'], eTrack)
                raise AssertionError("something wrong in status, electionTracker is off. " + str(check['electionTracker']))  
        return 'done'

    ####### THE MEAT & POTATOES ##########
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    check = a.client_call_for_http('setup/1/5')
    if check != 'confirm':
        raise AssertionError('setup Error: ' + str(check))

    waitForIt()
    a.ids = a.client_call_for_http(f'client/join_game/{a.name}')
    a.id = int(a.ids)
    waitForIt()
    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    waitForIt()
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    waitForIt()
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    waitForIt()
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)
    waitForIt()

    x = TestPlayer('frank')
    check = x.client_call_for_http(f'client/join_game/{x.name}')
    if "Unable to join, game is full." != check:
        raise AssertionError("frank wasn't supposed to be able to join." + x.text)

    waitForIt()

    x = input('''HOLDING: run /shs/server/quickDebug.py - mockData1()\n
        Enter to confirm.''')
    waitForIt()
    try:
        statusInfoCheck5player1(3, "The current President is a. Waiting for the President to nominate a Chancellor.")
    except AssertionError as theProblem:
        raise theProblem
    waitForIt()

    ###########START OF GAME LOOP##################
    # turn 1: a is president, a elections b, all vote ya, a gives b 1 lib/1 fas, b choses the fascist. 1 bad policy.
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    others = [b, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = a.client_call_for_http(f'client/nominate_chancellor_order/{a.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{a.name} nominated {b.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {a.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {a.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/president_play/{a.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {b.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections c, all vote ya, b gives c 1 lib/1 fas, c choses the fas. 2 bad policies.
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    others = [a, c, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if a.ids in check:
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{b.name} nominated {c.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.", fasCount=1, libCount=0)

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {b.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {b.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/president_play/{b.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {c.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 3: c is president, c elections d, all vote ya, c gives d 1 lib/1 fas, d choses the fas. c gets to policy peek.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    others = [a, b, d, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if b.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.", libCount=0, fasCount=2)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/president_play/{c.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/chancellor_play/{d.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt')
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt')
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt')
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(16, "The President will now look at the top 3 policy cards in the Policy Deck.", fasCount=3, libCount=0)

    checkAgainst = {'information': "The President will now look at the top 3 policy cards in the Policy Deck."}
    waitForIt()
    if a.client_call_for_json(f'client/president_policy_peek/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_policy_peek/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = c.client_call_for_json(f'client/president_policy_peek/{c.ids}')
        if len(check) != 4 or not (check['1'] != "Liberal" or check['1'] != "Fascist") or not (check['2'] != "Liberal" or check['2'] != "Fascist") or not (check['3'] != "Liberal" or check['3'] != "Fascist") or check['information'] != "You may now peek at the next three policy cards in the policy deck.":
            raise AssertionError('policy peek not working, ' + str(check))
    except KeyError:
        raise AssertionError('not all cards present in president policy peek' + str(check))
    waitForIt()
    if d.client_call_for_json(f'client/president_policy_peek/{d.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_json(f'client/president_policy_peek/{e.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = c.client_call_for_http(f'client/president_policy_peek_confirm/{c.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)


    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')

    ###########START OF GAME LOOP##################
    # turn 4: d is president, d elections a, all vote ya, d gives a 1 lib/1 fas, a choses the fas. d gets execution power 1, shoots a.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [a, b, c, e]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if c.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{a.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {a.name} for Chancellor.", libCount=0, fasCount=3)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {d.name} and Chancellor {a.name} will now enact a policy decision.")

    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/president_play/{d.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = a.client_call_for_http(f'client/chancellor_play/{a.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt')
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt')
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt')
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(17, "The President must now select a player to execute.", fasCount=4, libCount=0)

    checkAgainst = {'information': "The President must now select a player to execute."}
    waitForIt()
    if a.client_call_for_json(f'client/president_execute/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_execute/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = d.client_call_for_json(f'client/president_execute/{d.ids}')
        if check != {'information': "You must now execute a player.",
                     a.ids: a.name,
                     b.ids: b.name,
                     c.ids: c.name,
                     e.ids: e.name}:
            raise AssertionError('execution selection page not working, ' + str(check))
    except KeyError:
        raise AssertionError('eligible list likely wrong' + str(check))
    waitForIt()
    if c.client_call_for_json(f'client/president_execute/{c.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_json(f'client/president_execute/{e.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = d.client_call_for_http(f'client/president_execute_order/{d.ids}/{a.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)


    waitForIt()
    statusInfoCheck5player1(3, f"The President has selected {a.name} for immediate execution.")

    ###########START OF GAME LOOP##################
    # turn 5: a is dead, e is president, e elections b, all vote ya, e gives b 1 lib/1 fas, b choses the fas. e gets execution power 2, shoots b.
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    others = [c, b, d]
    for i in others:
        print(i.ids, i.id)
        if i.ids not in check:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem1")
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem2")
    # if c.ids in check or e.ids in check: # b is term limited, previous president
    #     raise AssertionError("former president should not be available for nomination.")
    if a.ids in check:
        raise AssertionError("dead men don't run for chancellor...")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = e.client_call_for_http(f'client/nominate_chancellor_order/{e.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{e.name} nominated {b.name} for Chancellor.", libCount=0, fasCount=4)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    # Can no longer vote
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    statusInfoCheck5player1(99, f"Vote passed. President {e.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {e.name} and Chancellor {b.name} will now enact a policy decision.")

    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {e.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = e.client_call_for_http(f'client/president_play/{e.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': ''}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError(check)
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {b.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!")

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    check = b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    waitForIt()
    if check != 'confirm':
        raise AssertionError('revolt: ' + check)
    waitForIt()
    if a.client_call_for_http(f'client/policy_result_confirm/{a.ids}') != 'confirm':
        raise AssertionError('revolt: ' + check)
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_confirm/{c.ids}') != 'confirm':
        raise AssertionError('revolt: ' + check)
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_confirm/{d.ids}') != 'confirm':
        raise AssertionError('revolt: ' + check)
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_confirm/{e.ids}') != 'moving to Executive Powers':
        raise AssertionError('revolt: ' + check)
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(17, "The President must now select a player to execute.", fasCount=5, libCount=0)

    checkAgainst = {'information': "The President must now select a player to execute."}
    waitForIt()
    if a.client_call_for_json(f'client/president_execute/{a.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_json(f'client/president_execute/{b.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    try:
        check = e.client_call_for_json(f'client/president_execute/{e.ids}')
        if check != {'information': "You must now execute a player.",
                     b.ids: b.name,
                     c.ids: c.name,
                     d.ids: d.name}:
            raise AssertionError('execution selection page not working, ' + str(check))
    except KeyError:
        raise AssertionError('eligible list likely wrong' + str(check))
    waitForIt()
    if c.client_call_for_json(f'client/president_execute/{c.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_json(f'client/president_execute/{d.ids}') != checkAgainst:
        raise AssertionError('revolt')
    waitForIt()

    waitForIt()
    check = e.client_call_for_http(f'client/president_execute_order/{e.ids}/{b.ids}')
    if check != 'confirm':
        raise AssertionError('something wrong with policy peek confirmation, ' + check)

    waitForIt()
    statusInfoCheck5player1(3, f"The President has selected {b.name} for immediate execution.")

    ###########START OF GAME LOOP##################
    # turn 6: a and b are dead, c is president, c elections d, all vote ya, c gives d 2 fas, d requests veto, c consents, etrack up 1.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    print(check)
    others = [d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    if a.ids in check or b.ids in check:
        raise AssertionError("dead men don't run for chancellor...")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    # b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {"c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {c.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/president_play/{c.ids}/Fascist/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'1': "Fascist", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': True, 'vetoText': "You may veto these policies if the President consents."}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/chancellor_veto/{d.ids}')
    if check != "Awaiting president response":
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor veto")

    statusInfoCheck5player1(11, "The Chancellor has requested to veto the current agenda.")

    checkAgainst = "Awaiting president response"
    check = a.client_call_for_http(f'client/president_veto/{a.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = b.client_call_for_http(f'client/president_veto/{b.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = d.client_call_for_http(f'client/president_veto/{d.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = e.client_call_for_http(f'client/president_veto/{e.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = c.client_call_for_http(f'client/president_veto/{c.ids}')
    if check != f"Chancellor {d.name} has requested to veto the current set of policies. Do you accept?":
        raise AssertionError('mutiny in pres president_veto')
    check = c.client_call_for_http(f'client/president_veto_choice/{c.ids}/{1}')
    if check != "veto successful":
        raise AssertionError('something wrong with president_veto_choice')

    statusInfoCheck5player1(13, f'President {c.name} and Chancellor {d.name} have decided to veto the current agenda. The election tracker will increase by 1.', eTrack=1)

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')
    
    ###########START OF GAME LOOP##################
    # turn 7: a and b are dead, d is president, d elections c, all vote ya, d gives c 2 fas, c requests veto, d refuses, final fas played, game over.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [c, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    if a.ids in check or b.ids in check:
        raise AssertionError("dead men don't run for chancellor...")
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {c.name} for Chancellor.")
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    waitForIt()
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    # b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    checkAgainst = {"c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {d.name} and Chancellor {c.name} will now enact a policy decision.")

    waitForIt()
    check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()
    check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()
    check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()    
    waitForIt()
    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if check != {'wait': f"Waiting for President {d.name} to select policies."}:
        raise AssertionError()
    waitForIt()

    check = d.client_call_for_http(f'client/president_play/{d.ids}/Fascist/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

    statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Fascist", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': True, 'vetoText': "You may veto these policies if the President consents."}:
        print(check)
        raise AssertionError('chancellor draw problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError(str(check))
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': f"Waiting for Chancellor {c.name} to select a policy."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_veto/{c.ids}')
    if check != "Awaiting president response":
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor veto")

    statusInfoCheck5player1(11, "The Chancellor has requested to veto the current agenda.")

    checkAgainst = "Awaiting president response"
    check = a.client_call_for_http(f'client/president_veto/{a.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = b.client_call_for_http(f'client/president_veto/{b.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = c.client_call_for_http(f'client/president_veto/{c.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = e.client_call_for_http(f'client/president_veto/{e.ids}')
    if check != checkAgainst:
        raise AssertionError('mutiny in non-pres president veto')
    check = d.client_call_for_http(f'client/president_veto/{d.ids}')
    if check != f"Chancellor {c.name} has requested to veto the current set of policies. Do you accept?":
        raise AssertionError('mutiny in pres president_veto')
    check = d.client_call_for_http(f'client/president_veto_choice/{d.ids}/{0}')
    if check != "veto denied":
        raise AssertionError('something wrong with president_veto_choice')

    statusInfoCheck5player1(12, "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact.", eTrack=0)

    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Fascist", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': "The President has declined your request to veto. You MUST select a policy to enact."}:
        print(check)
        raise AssertionError('chancellor draw (FORCED) problem')
    check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    if check != {'wait': "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact."}:
        raise AssertionError(str(check))
    waitForIt()
    check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    if check != {'wait': "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact."}:
        raise AssertionError()
    waitForIt()
    check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    if check != {'wait': "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact."}:
        raise AssertionError()
    waitForIt()
    check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    if check != {'wait': "The President has declined the Chancellor's request to veto the current agenda. The Chancellor MUST select a policy to enact."}:
        raise AssertionError()
    waitForIt()

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Fascist/Liberal')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    statusInfoCheck5player1(97, "A Fascist policy was enacted!", libCount=0, fasCount=6)

    waitForIt()
    if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()
    if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
        raise AssertionError('revolt')
    waitForIt()

    a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(100, "The Fascists have achieved a policy victory.")

    check = a.client_call_for_json('client/game_over')
    checkAgainst = {'a': 'a : Liberal : Dead',
                    'b': 'b : Liberal : Dead',
                    'c': 'c : Liberal : Alive',
                    'd': 'd : Fascist : Alive',
                    'e': 'e : Hitler : Alive',
                    'fasPolicyCount': 6,
                    'libPolicyCount': 0,
                    'whatHappened': "The Fascists have achieved a policy victory."}
    if checkAgainst != check:
        raise AssertionError('end game text wrong: ' + str(check))
    print('done')

def testGame5():
    """5 player test game, responding solely to Http/Json information from server. Quick test confirming election Tracker functions work accurately."""

    ###### LOCAL HELPERS ######
    def statusInfoCheck5player1(currentID, currentMessage, libCount=None, fasCount=None, eTrack=None):
        check = a.client_call_for_json(f'client/client_status/{a.ids}')
        if check['name'] != 'a' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check) + "\n" + currentMessage)
        check = b.client_call_for_json(f'client/client_status/{b.ids}')
        if check['name'] != 'b' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = c.client_call_for_json(f'client/client_status/{c.ids}')
        if check['name'] != 'c' or check['party'] != 'Liberal' or check['role'] != 'Liberal' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or "Other Fascists" in check:
            raise AssertionError("something wrong with get_status()" + str(check))
        check = d.client_call_for_json(f'client/client_status/{d.ids}')
        if check['name'] != 'd' or check['party'] != 'Fascist' or check['role'] != 'Fascist' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Hitler'] != 'e' or check['Other Fascists'] != "d":
            raise AssertionError("something wrong with get_status()" + str(check))
        check = e.client_call_for_json(f'client/client_status/{e.ids}')
        try:
            if check['name'] != 'e' or check['party'] != 'Fascist' or check['role'] != 'Hitler' or check['statusID'] != currentID or check['statusUpdate'] != currentMessage or check['Other Fascists'] != "d":
                raise AssertionError("something wrong with get_status()" + str(check))
        except KeyError:
            raise KeyError('huh? :' + str(check))
        if libCount != None:
            if check["libPolicies"] != libCount:
                raise AssertionError("something wrong in status, too few liberal policies on count")
        if fasCount != None:
            if check["fasPolicies"] != fasCount:
                raise AssertionError("something wrong in status, too few fascist policies on count")  
        if eTrack != None:
            if check['electionTracker'] != eTrack:
                raise AssertionError("something wrong in status, electionTracker is off. " + str(check['electionTracker']))  
        return 'done'

    ####### THE MEAT & POTATOES ##########
    a = TestPlayer('a')
    b = TestPlayer('b')
    c = TestPlayer('c')
    d = TestPlayer('d')
    e = TestPlayer('e')

    check = a.client_call_for_http('setup/1/5')
    if check != 'confirm':
        raise AssertionError('setup Error: ' + str(check))

    waitForIt()
    a.ids = a.client_call_for_http(f'client/join_game/{a.name}')
    a.id = int(a.ids)
    waitForIt()
    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    waitForIt()
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    waitForIt()
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    waitForIt()
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)
    waitForIt()

    x = TestPlayer('frank')
    check = x.client_call_for_http(f'client/join_game/{x.name}')
    if "Unable to join, game is full." != check:
        raise AssertionError("frank wasn't supposed to be able to join." + x.text)

    waitForIt()

    x = input('''HOLDING: run /shs/server/quickDebug.py - mockData1()\n
        Enter to confirm.''')
    waitForIt()
    try:
        statusInfoCheck5player1(3, "The current President is a. Waiting for the President to nominate a Chancellor.")
    except AssertionError as theProblem:
        raise theProblem
    waitForIt()

    ###########START OF GAME LOOP##################
    # turn 1: a is president, a elections b, all vote against, track goes up by 1.
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    others = [b, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = a.client_call_for_http(f'client/nominate_chancellor_order/{a.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{a.name} nominated {b.name} for Chancellor.", eTrack=0)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # Less than half vote ja, a majority is required.
    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/0')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/0')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/0')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    waitForIt()
    waitForIt()
    waitForIt()
    statusInfoCheck5player1(98, f"The election has failed. The election tracker will increase by 1.", eTrack=1)

    waitForIt()
    checkAgainst = {'a': False, 'b': False, "c": False, 'd': True, 'e': True, 'result': 'The vote failed. Citizen frustration will increase.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(3, "The current President is b. Waiting for the President to nominate a Chancellor.")

    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections a, all vote against, track goes up by 1.
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    others = [a, c, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{a.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{b.name} nominated {a.name} for Chancellor.", eTrack=1)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # Less than half vote ja, a majority is required.
    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/0')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/0')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/0')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/0')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(98, f"The election has failed. The election tracker will increase by 1.", eTrack=2)

    waitForIt()
    checkAgainst = {'a': False, 'b': False, "c": False, 'd': False, 'e': True, 'result': 'The vote failed. Citizen frustration will increase.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(3, "The current President is c. Waiting for the President to nominate a Chancellor.")

    ###########START OF GAME LOOP##################
    # turn 3: c is president, c elections b, all vote against, track goes up by 1.
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    others = [b, a, d, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{b.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{c.name} nominated {b.name} for Chancellor.", eTrack=2)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # Less than half vote ja, a majority is required.
    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/0')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/0')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/0')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/0')
    waitForIt()

    '''Election fails, the election tracker pushes up to 3, a policy is pulled
    of the top of the deck and played, the election tracker goes back to 0.'''
    try:
        statusInfoCheck5player1(98, f"The election has failed. The election tracker will increase by 1. The people have enacted a Liberal policy!", eTrack=0)
    except AssertionError:
        statusInfoCheck5player1(98, f"The election has failed. The election tracker will increase by 1. The people have enacted a Fascist policy!", eTrack=0)


    waitForIt()
    checkAgainst = {'a': True, 'b': False, "c": False, 'd': False, 'e': False, 'result': 'The vote failed. Citizen frustration will increase.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(3, "The current President is d. Waiting for the President to nominate a Chancellor.")

    ###########START OF GAME LOOP##################
    # turn 4: d is president, d elections e, all vote against, track goes up by 1.
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    others = [b, c, a, e]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{e.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{d.name} nominated {e.name} for Chancellor.", eTrack=0)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # Less than half vote ja, a majority is required.
    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/0')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/0')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/0')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(98, f"The election has failed. The election tracker will increase by 1.", eTrack=1)

    waitForIt()
    checkAgainst = {'a': False, 'b': True, "c": False, 'd': False, 'e': True, 'result': 'The vote failed. Citizen frustration will increase.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(3, "The current President is e. Waiting for the President to nominate a Chancellor.")

    ###########START OF GAME LOOP##################
    # turn 5: e is president, e elections a, vote passes, track should be at 0 after election success.
    check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    others = [b, c, d, a]
    for i in others:
        if check[i.ids] != i.name:
            print('What was got', check)
            raise AssertionError("president's json nomination has problem")
    # TODO - Additional checks on received JSON should probably be made...
    check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    if check != {'wait': '1'}:
        raise AssertionError("problem with non-president json response.")
    waitForIt()
    check = e.client_call_for_http(f'client/nominate_chancellor_order/{e.ids}/{a.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()


    statusInfoCheck5player1(6, f"{e.name} nominated {a.name} for Chancellor.", eTrack=1)
    # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # Should be just enough votes to pass.
    waitForIt()
    a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/0')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/0')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()

    statusInfoCheck5player1(99, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.", eTrack=0)
    waitForIt()
    checkAgainst = {'a': True, 'b': False, "c": False, 'd': True, 'e': True, 'result': 'The vote passed.'}
    check = a.client_call_for_json(f'client/show_all_votes')
    if check != checkAgainst:
        raise AssertionError('vote check problem. ' + str(check))
    waitForIt()
    check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    if check != 'confirm':
        raise AssertionError('vote check confirmation problem. ' + str(check))
    waitForIt()

    statusInfoCheck5player1(9, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.")

    check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    if len(check) != 4:
        print(check)
        raise AssertionError("check the president draw cards, something is probably wrong.")
    waitForIt()

    print('done')

def waitForIt(doWait=False):
    if doWait:
        x = input('')
        return
    else:
        time.sleep(1)
        return



if __name__ == '__main__':
    testGame1()
    testGame2()
    testGame3()
    testGame4()
    testGame5()