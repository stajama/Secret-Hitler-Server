from ClientObject import TestPlayer

import time

def appTestHelper1():

    app = TestPlayer('Stamos')
    b = TestPlayer('Byron')
    c = TestPlayer('Charles')
    d = TestPlayer('Daniel')
    e = TestPlayer('Eric')


    pauseForAppTesting("start game and join first")

    b.ids = b.client_call_for_http(f'client/join_game/{b.name}')
    b.id = int(b.ids)
    app.id = b.id - 1
    app.ids = str(app.id)
    c.ids = c.client_call_for_http(f'client/join_game/{c.name}')
    c.id = int(c.ids)
    d.ids = d.client_call_for_http(f'client/join_game/{d.name}')
    d.id = int(d.ids)
    e.ids = e.client_call_for_http(f'client/join_game/{e.name}')
    e.id = int(e.ids)

    ###########START OF GAME LOOP##################
    # turn 1: app is president, app elections b, all vote ya. Try to pass a Liberal policy if possible, script will adjust if not possible.
  
    pauseForAppTesting("select Byron for chancellor and vote yes")


    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')

   

    waitForIt()

    check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')


    pauseForAppTesting("Send cards to Byron")

    check = b.client_call_for_http(f'client/chancellor_play/{b.ids}/Liberal/Fascist')
    waitForIt()

    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    pauseForAppTesting("confirm policy result")
    
    ###########START OF GAME LOOP##################
    # turn 2: b is president, b elections c, all vote ya, b gives c 1 lib/1 fas, c choses the lib. All is well.

    check = b.client_call_for_http(f'client/nominate_chancellor_order/{b.ids}/{c.ids}')
    if check != "confirm":
        raise AssertionError('nomination order not confirmed')
    waitForIt()



    waitForIt()
    b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    waitForIt()
    c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    waitForIt()
    d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    waitForIt()
    e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    waitForIt()
    
    pauseForAppTesting("vote yes for President Byron and Chancellor Charles")

    pauseForAppTesting("confirm vote results")

    pauseForAppTesting("check app for wrong hidden information")

    check = b.client_call_for_http(f'client/president_play/{b.ids}/Liberal/Fascist/Liberal')
    if check != "confirm":
        print(check)
        raise AssertionError('president card selection problem')
    waitForIt()

   
    check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': '', "statusID": 10, "wait": ""}:
        print(check)
        raise AssertionError('chancellor draw problem')

    pauseForAppTesting("waiting for chancellor check-app")

    check = c.client_call_for_http(f'client/chancellor_play/{c.ids}/Liberal/Fascist')
    if check != 'confirm':
        print("error headsup", check)
        raise AssertionError("something wrong with chancellor play")

    pauseForAppTesting("look at confirmation page.")

    b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    waitForIt()

    waitForIt()
    statusInfoCheck5player1(3, f'The current President is {c.name}. Waiting for the President to nominate a Chancellor.')
    
    # ###########START OF GAME LOOP##################
    # # turn 3: c is president, c elections d, all vote ya, c gives d 1 lib/1 fas, d choses the lib. All is well.
    # check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    # others = [a, b, d, e]
    # for i in others:
    #     print(i.ids, i.id)
    #     if i.ids not in check:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem1")
    #     if check[i.ids] != i.name:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem2")
    # # if b.ids in check: # b is term limited, previous president
    # #     raise AssertionError("former president should not be available for nomination.")
    # # TODO - Additional checks on received JSON should probably be made...
    # check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # waitForIt()
    # check = c.client_call_for_http(f'client/nominate_chancellor_order/{c.ids}/{d.ids}')
    # if check != "confirm":
    #     raise AssertionError('nomination order not confirmed')
    # waitForIt()


    # statusInfoCheck5player1(6, f"{c.name} nominated {d.name} for Chancellor.", libCount=2)
    # # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # waitForIt()
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    # waitForIt()
    # b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    # waitForIt()
    # c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    # waitForIt()
    # d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    # waitForIt()
    # e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    # waitForIt()

    # waitForIt()
    # waitForIt()
    # statusInfoCheck5player1(99, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    # waitForIt()
    # checkAgainst = {'number of votes': 5, 'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.'}
    # check = a.client_call_for_json(f'client/show_all_votes')
    # if check != checkAgainst:
    #     raise AssertionError('vote check problem. ' + str(check))
    # waitForIt()
    # check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()

    # statusInfoCheck5player1(9, f"Vote passed. President {c.name} and Chancellor {d.name} will now enact a policy decision.")

    # waitForIt()
    # check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    # if check['wait'] != "" or check['information'] != 'Select a policy card to discard. The remaining cards will be passed to the Chancellor.' or \
    #         check["statusID"] != 9 or not (check["1"] == "Liberal" or check["1"] == "Fascist") or \
    #         not (check["2"] == "Liberal" or check["2"] == "Fascist") or \
    #         not (check["3"] == "Liberal" or check["3"] == "Fascist"):        
    #     print(check)
    #     raise AssertionError("check the president draw cards, something is probably wrong.")
    # waitForIt()
    # check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    # if check != {'wait': f"Waiting for President {c.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    # if check != {'wait': f"Waiting for President {c.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    # if check != {'wait': f"Waiting for President {c.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()    
    # waitForIt()
    # check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    # if check != {'wait': f"Waiting for President {c.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()

    # check = c.client_call_for_http(f'client/president_play/{c.ids}/Liberal/Fascist/Liberal')
    # if check != "confirm":
    #     print(check)
    #     raise AssertionError('president card selection problem')
    # waitForIt()

    # statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    # check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    # if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': '', "statusID": 10, 'wait': ''}:
    #     print(check)
    #     raise AssertionError('chancellor draw problem')
    # check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    # if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(str(check))
    # waitForIt()
    # check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    # if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(check)
    # waitForIt()
    # check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    # if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()
    # check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    # if check != {'wait': f"Waiting for Chancellor {d.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()

    # check = d.client_call_for_http(f'client/chancellor_play/{d.ids}/Liberal/Fascist')
    # if check != 'confirm':
    #     print("error headsup", check)
    #     raise AssertionError("something wrong with chancellor play")

    # statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    # waitForIt()
    # if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()

    # a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    # b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    # c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    # d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    # e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    # waitForIt()

    # waitForIt()
    # statusInfoCheck5player1(3, f'The current President is {d.name}. Waiting for the President to nominate a Chancellor.')

    # ###########START OF GAME LOOP##################
    # # turn 4: d is president, d elections e, all vote ya, d gives e 1 lib/1 fas, e choses the lib. All is well.
    # check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    # others = [a, b, c, e]
    # for i in others:
    #     print(i.ids, i.id)
    #     if i.ids not in check:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem1")
    #     if check[i.ids] != i.name:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem2")
    # # if c.ids in check: # b is term limited, previous president
    # #     raise AssertionError("former president should not be available for nomination.")
    # # TODO - Additional checks on received JSON should probably be made...
    # check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # waitForIt()
    # check = d.client_call_for_http(f'client/nominate_chancellor_order/{d.ids}/{e.ids}')
    # if check != "confirm":
    #     raise AssertionError('nomination order not confirmed')
    # waitForIt()


    # statusInfoCheck5player1(6, f"{d.name} nominated {e.name} for Chancellor.", libCount=3)
    # # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # waitForIt()
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    # waitForIt()
    # b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    # waitForIt()
    # c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    # waitForIt()
    # d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    # waitForIt()
    # e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    # waitForIt()

    # waitForIt()
    # waitForIt()
    # statusInfoCheck5player1(99, f"Vote passed. President {d.name} and Chancellor {e.name} will now enact a policy decision.")

    # waitForIt()
    # checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.', "number of votes": 5}
    # check = a.client_call_for_json(f'client/show_all_votes')
    # if check != checkAgainst:
    #     raise AssertionError('vote check problem. ' + str(check))
    # waitForIt()
    # check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()

    # statusInfoCheck5player1(9, f"Vote passed. President {d.name} and Chancellor {e.name} will now enact a policy decision.")

    # waitForIt()
    # check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    # if check['wait'] != "" or check['information'] != 'Select a policy card to discard. The remaining cards will be passed to the Chancellor.' or \
    #         check["statusID"] != 9 or not (check["1"] == "Liberal" or check["1"] == "Fascist") or \
    #         not (check["2"] == "Liberal" or check["2"] == "Fascist") or \
    #         not (check["3"] == "Liberal" or check["3"] == "Fascist"):
    #     print(check)
    #     raise AssertionError("check the president draw cards, something is probably wrong.")
    # waitForIt()
    # check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    # if check != {'wait': f"Waiting for President {d.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    # if check != {'wait': f"Waiting for President {d.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    # if check != {'wait': f"Waiting for President {d.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()    
    # waitForIt()
    # check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    # if check != {'wait': f"Waiting for President {d.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()

    # check = d.client_call_for_http(f'client/president_play/{d.ids}/Liberal/Fascist/Liberal')
    # if check != "confirm":
    #     print(check)
    #     raise AssertionError('president card selection problem')
    # waitForIt()

    # statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    # check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    # if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': '', "statusID": 10, 'wait': ''}:
    #     print(check)
    #     raise AssertionError('chancellor draw problem')
    # check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    # if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(str(check))
    # waitForIt()
    # check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    # if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(check)
    # waitForIt()
    # check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    # if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()
    # check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    # if check != {'wait': f"Waiting for Chancellor {e.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()

    # check = e.client_call_for_http(f'client/chancellor_play/{e.ids}/Liberal/Fascist')
    # if check != 'confirm':
    #     print("error headsup", check)
    #     raise AssertionError("something wrong with chancellor play")

    # statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    # waitForIt()
    # if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()

    # a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    # b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    # c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    # d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    # e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    # waitForIt()

    # waitForIt()
    # statusInfoCheck5player1(3, f'The current President is {e.name}. Waiting for the President to nominate a Chancellor.')

    # ###########START OF GAME LOOP##################
    # # turn 5: e is president, e elections a, all vote ya, e gives a 1 lib/1 fas, a choses the lib. Liberals win.
    # check = e.client_call_for_json(f'client/nominate_chancellor/{e.ids}')
    # others = [a, c, b, d]
    # for i in others:
    #     print(i.ids, i.id)
    #     if i.ids not in check:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem1")
    #     if check[i.ids] != i.name:
    #         print('What was got', check)
    #         raise AssertionError("president's json nomination has problem2")
    # # if d.ids in check: # d is term limited, previous president
    # #     raise AssertionError("former president should not be available for nomination.")
    # # TODO - Additional checks on received JSON should probably be made...
    # check = a.client_call_for_json(f'client/nominate_chancellor/{a.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = b.client_call_for_json(f'client/nominate_chancellor/{b.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = d.client_call_for_json(f'client/nominate_chancellor/{d.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # check = c.client_call_for_json(f'client/nominate_chancellor/{c.ids}')
    # if check != {'wait': '1'}:
    #     raise AssertionError("problem with non-president json response.")
    # waitForIt()
    # check = e.client_call_for_http(f'client/nominate_chancellor_order/{e.ids}/{a.ids}')
    # if check != "confirm":
    #     raise AssertionError('nomination order not confirmed')
    # waitForIt()


    # statusInfoCheck5player1(6, f"{e.name} nominated {a.name} for Chancellor.", libCount=4)
    # # updateGStatusUpdate(f"{findCurrentPresident().name} nominated {Player.objects.get(pk=selected).name} for Chancellor.")

    # waitForIt()
    # a.client_call_for_http(f'client/submit_vote/{a.ids}/1')
    # waitForIt()
    # b.client_call_for_http(f'client/submit_vote/{b.ids}/1')
    # waitForIt()
    # c.client_call_for_http(f'client/submit_vote/{c.ids}/1')
    # waitForIt()
    # d.client_call_for_http(f'client/submit_vote/{d.ids}/1')
    # waitForIt()
    # e.client_call_for_http(f'client/submit_vote/{e.ids}/1')
    # waitForIt()

    # waitForIt()
    # waitForIt()
    # statusInfoCheck5player1(99, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.")

    # waitForIt()
    # checkAgainst = {'a': True, 'b': True, "c": True, 'd': True, 'e': True, 'result': 'The vote passed.', "number of votes": 5}
    # check = a.client_call_for_json(f'client/show_all_votes')
    # if check != checkAgainst:
    #     raise AssertionError('vote check problem. ' + str(check))
    # waitForIt()
    # check = a.client_call_for_http(f'client/vote_show_confirmation/{a.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = b.client_call_for_http(f'client/vote_show_confirmation/{b.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = c.client_call_for_http(f'client/vote_show_confirmation/{c.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = d.client_call_for_http(f'client/vote_show_confirmation/{d.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()
    # check = e.client_call_for_http(f'client/vote_show_confirmation/{e.ids}')
    # if check != 'confirm':
    #     raise AssertionError('vote check confirmation problem. ' + str(check))
    # waitForIt()

    # statusInfoCheck5player1(9, f"Vote passed. President {e.name} and Chancellor {a.name} will now enact a policy decision.")

    # waitForIt()
    # check = e.client_call_for_json(f'client/president_draw/{e.ids}')
    # if check['wait'] != "" or check['information'] != 'Select a policy card to discard. The remaining cards will be passed to the Chancellor.' or \
    #         check["statusID"] != 9 or not (check["1"] == "Liberal" or check["1"] == "Fascist") or \
    #         not (check["2"] == "Liberal" or check["2"] == "Fascist") or \
    #         not (check["3"] == "Liberal" or check["3"] == "Fascist"):        
    #     print(check)
    #     raise AssertionError("check the president draw cards, something is probably wrong.")
    # waitForIt()
    # check = a.client_call_for_json(f'client/president_draw/{a.ids}')
    # if check != {'wait': f"Waiting for President {e.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = b.client_call_for_json(f'client/president_draw/{b.ids}')
    # if check != {'wait': f"Waiting for President {e.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()
    # check = d.client_call_for_json(f'client/president_draw/{d.ids}')
    # if check != {'wait': f"Waiting for President {e.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()    
    # waitForIt()
    # check = c.client_call_for_json(f'client/president_draw/{c.ids}')
    # if check != {'wait': f"Waiting for President {e.name} to select policies.", "statusID": 9}:
    #     raise AssertionError()
    # waitForIt()

    # check = e.client_call_for_http(f'client/president_play/{e.ids}/Liberal/Fascist/Liberal')
    # if check != "confirm":
    #     print(check)
    #     raise AssertionError('president card selection problem')
    # waitForIt()

    # statusInfoCheck5player1(10, 'Waiting for the Chancellor to select a policy.')

    # check = a.client_call_for_json(f'client/chancellor_draw/{a.ids}')
    # if check != {'1': "Liberal", "2": "Fascist", 'information': "Select a policy card to enact.", 'veto': False, 'vetoText': '', "statusID": 10, 'wait': ''}:
    #     print(check)
    #     raise AssertionError('chancellor draw problem')
    # check = d.client_call_for_json(f'client/chancellor_draw/{d.ids}')
    # if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(str(check))
    # waitForIt()
    # check = b.client_call_for_json(f'client/chancellor_draw/{b.ids}')
    # if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError(check)
    # waitForIt()
    # check = c.client_call_for_json(f'client/chancellor_draw/{c.ids}')
    # if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()
    # check = e.client_call_for_json(f'client/chancellor_draw/{e.ids}')
    # if check != {'wait': f"Waiting for Chancellor {a.name} to select a policy.", "statusID": 10}:
    #     raise AssertionError()
    # waitForIt()

    # check = a.client_call_for_http(f'client/chancellor_play/{a.ids}/Liberal/Fascist')
    # if check != 'confirm':
    #     print("error headsup", check)
    #     raise AssertionError("something wrong with chancellor play")

    # statusInfoCheck5player1(97, "A Liberal policy was enacted!")

    # waitForIt()
    # if a.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if b.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if c.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if d.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()
    # if e.client_call_for_http(f'client/policy_result_review') != 'confirm':
    #     raise AssertionError('revolt')
    # waitForIt()

    # a.client_call_for_http(f'client/policy_result_confirm/{a.ids}')
    # waitForIt()
    # b.client_call_for_http(f'client/policy_result_confirm/{b.ids}')
    # waitForIt()
    # c.client_call_for_http(f'client/policy_result_confirm/{c.ids}')
    # waitForIt()
    # d.client_call_for_http(f'client/policy_result_confirm/{d.ids}')
    # waitForIt()
    # e.client_call_for_http(f'client/policy_result_confirm/{e.ids}')
    # waitForIt()

    # statusInfoCheck5player1(100, "The Liberals have achieved a policy victory.", libCount=5)
    # waitForIt()
    # for playerPlayer in [a, b, c, d, e]:
    #     check = playerPlayer.client_call_for_json('client/game_over')
    #     if check != {'a': 'a : Liberal : Alive',
    #                  'b': 'b : Liberal : Alive',
    #                  'c': 'c : Liberal : Alive',
    #                  'd': 'd : Fascist : Alive',
    #                  'e': 'e : Hitler : Alive',
    #                  'fasPolicyCount': 0,
    #                  'libPolicyCount': 5,
    #                  'whatHappened': "The Liberals have achieved a policy victory."}:
    #         raise AssertionError('something wrong with end results page: ' + str(check))

    print('done')

def pauseForAppTesting(message=None):
    if message == None:
        message = ""
    input(message)
    return

def waitForIt():
    time.sleep(2)
    return

if __name__ == '__main__':
    appTestHelper1()