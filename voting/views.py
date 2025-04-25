from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required
def vote_view(request):
    user_id = request.user.id

    with connection.cursor() as cursor:
        # Load all available sessions
        cursor.execute("SELECT id, title FROM sessions")
        sessions = cursor.fetchall()

        # Load all cards
        cursor.execute("SELECT id, title FROM cards")
        cards = cursor.fetchall()

    if request.method == 'POST':
        session_id = request.POST.get('session_id')

        # Check if this user already voted in that session
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM votes WHERE user_id=%s AND session_id=%s",
                [user_id, session_id]
            )
            already_voted = cursor.fetchone()[0]

        if already_voted:
            return render(request, 'voting/vote.html', {
                'already_voted': True,
                'sessions': sessions,
                'cards': cards
            })

        # Save new votes
        with connection.cursor() as cursor:
            for key in request.POST:
                if key.startswith('card_'):
                    card_id = key.split('_')[1]
                    vote = request.POST[key]
                    comment = request.POST.get(f'comment_{card_id}', '')
                    cursor.execute(
                        "INSERT INTO votes (user_id, session_id, card_id, vote, comment) VALUES (%s, %s, %s, %s, %s)",
                        [user_id, session_id, card_id, vote, comment]
                    )

        return render(request, 'voting/vote.html', {
            'submitted': True,
            'sessions': sessions,
            'cards': cards
        })

    return render(request, 'voting/vote.html', {
        'sessions': sessions,
        'cards': cards
    })
