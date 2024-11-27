from django.contrib import admin

from train_station.models import (
    Crew,
    Train,
    TrainType,
    Station,
    Route,
    Trip,
    Order,
    Ticket,
)

admin.site.register(Crew)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(Order)
admin.site.register(Ticket)
