from django.urls import path

from . import views

urlpatterns = [
    path('get', views.get, name="get"),
    path('setup/<int:confirm>/<int:playerCount>', views.setup),
    path('client/join_game/<str:pname>', views.joinGame),
    path('client/client_status/<int:id>', views.client_status),
    path('client/heads_up', views.headsUpToVote),
    path('client/submit_vote/<int:id>/<int:voting>', views.submitVote),
    path('client/show_all_votes', views.showEveryonesVotes),
    path('client/vote_show_confirmation/<int:id>', views.showEveryonesVotesConfirm),
    path('client/president_draw/<int:id>', views.policyPresidentDraw),
    path('client/president_play/<int:id>/<str:passing1>/<str:passing2>/<str:discarded>', views.policyPresidentSelect),
    path('client/chancellor_draw/<int:id>', views.policyChancellorDraw),
    path('client/chancellor_play/<int:id>/<str:passCard>/<str:discard>', views.policyChancellorSelects),
    path('client/chancellor_veto/<int:id>', views.policyChancellorVeto),
    path('client/president_veto/<int:id>', views.policyVetoPresident),
    path('client/president_veto_choice/<int:id>/<int:choice>', views.policyVetoChoice),
    # path('client/chancellor_must_play/<int:id>', views.forcedChancellor),
    path('client/president_execute/<int:id>', views.executiveExecution),
    path('client/president_execute_order/<int:id>/<int:selected>', views.executiveExecutionOrder),
    path('client/president_party_peek/<int:id>', views.executiveAffiliationLook),
    path('client/president_party_peek_order/<int:id>/<int:selected>', views.executiveAffiliationLookOrder),
    path('client/president_policy_peek/<int:id>', views.executivePolicyPeek),
    path('client/president_special_election/<int:id>', views.executiveSpecialElection),
    path('client/president_special_election_order/<int:id>/<int:selected>', views.executiveSpecialElectionOrder),
    path('client/get_status/<int:id>', views.getStatus),
    # path('client/role_info/<int:id>', views.roleSpecificRequest),
    path('client/nominate_chancellor/<int:id>', views.nominateChancellor),
    path('client/nominate_chancellor_order/<int:id>/<int:selected>', views.nominateChancellorOrder),
    path('client/policy_result_review', views.policyResultsView),
    path('client/policy_result_confirm/<int:id>', views.policyResultsConfirm),
    path('client/game_over', views.gameIsOver),
    path('client/president_policy_peek_confirm/<int:id>', views.executivePolicyPeekConfirmation),

    # extra URLs for debugging.
    path('debug/mockData1', views.mockData1),
    path('debug/mockData2', views.mockData2),
    path('debug/mockData3', views.mockData3),

]