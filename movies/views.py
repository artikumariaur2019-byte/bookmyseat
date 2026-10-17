from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie, Theater, Seat, Booking, Review
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages

def movie_list(request):
    search_query=request.GET.get('search')
    if search_query:
        movies=Movie.objects.filter(name__icontains=search_query)
    else:
        movies=Movie.objects.all()
    return render(request,'movies/movie_list.html',{'movies':movies})

def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})



@login_required(login_url='/login/')
def book_seats(request,theater_id):
    theaters=get_object_or_404(Theater,id=theater_id)
    seats=Seat.objects.filter(theater=theaters)
    if request.method=='POST':
        selected_Seats = [
        seat_id
        for seat_id in request.POST.getlist('seats')
        if seat_id.isdigit()
    ]
        error_seats = []
        
        if not selected_Seats:
            return render(request,"movies/seat_selection.html",{'theater':theaters,"seats":seats,'error':"No seat selected"})
        for seat_id in selected_Seats:
            seat=get_object_or_404(Seat,id=seat_id,theater=theaters)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user= request.user,
                    seat=seat,
                    movie=theaters.movie,
                    theater=theaters
                )
                seat.is_booked=True
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)
        if error_seats:
            error_message=(f"The following seats are already booked:{','.join(error_seats)}")

            return render(request,'movies/seat_selection.html',{'theater':theaters,"seats":"seats",'error':"No seat selected"})
        return redirect('profile')            

    return render(request, 'movies/seat_selection.html', {'theaters':theaters, "seats":seats})




def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            movie=movie,
            user=request.user
        ).first()

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': movie,
            'user_review': user_review,
        }
    )




@login_required(login_url='/login/')
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    has_booking = Booking.objects.filter(
        user=request.user,
        movie=movie
    ).exists()

    if not has_booking:
        messages.error(request, "Please book this movie before submitting a review.")
        return redirect('movie_detail', movie_id=movie.id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 0

        if 1 <= rating <= 5 and comment:
            Review.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            messages.success(request, "Your review has been submitted successfully!")
        else:
            messages.error(request, "Please select a rating from 1 to 5 and write a review.")

    return redirect('movie_detail', movie_id=movie.id)



@login_required(login_url='/login/')
def delete_review(request, movie_id, review_id):
    movie = get_object_or_404(Movie, id=movie_id)

    review = get_object_or_404(
        Review,
        id=review_id,
        movie=movie,
        user=request.user
    )

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Your review has been deleted successfully!")

    return redirect('movie_detail', movie_id=movie.id)

