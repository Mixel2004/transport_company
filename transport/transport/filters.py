from rest_framework import filters

# class RoleFilterBackend(filters.BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         role = request.query_params.get('role')
#         if role:
#             return queryset.filter(role=role)
#         return queryset

class CurrentLocationFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        location = request.query_params.get('current_location')
        if not location:
            return queryset
        try:
            location = int(location)
        except ValueError:
            location = location
        if type(location) == int:
            queryset = queryset.filter(current_location_id=location)
        elif type(location) == str:
            queryset = queryset.filter(current_location__name__iexact=location)
        
        return queryset

class CustomerFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        customer = request.query_params.get('customer')
        if customer:
            return queryset.filter(customer__email__iexact=customer)
        return queryset

