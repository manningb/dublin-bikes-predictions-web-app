var map, activeInfoWindow;
var markers = [];
var search_markers = [];
const myLatLng = {lat: 53.3531, lng: -6.2580};
const $info = document.getElementById('info');


const trackLocation = ({
                           onSuccess, onError = () => {
    }
                       }) => {
    // Omitted for brevity

    return navigator.geolocation.watchPosition(onSuccess, onError, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
};
const getPositionErrorMessage = code => {
    switch (code) {
        case 1:
            return 'Permission denied.';
        case 2:
            return 'Position unavailable.';
        case 3:
            return 'Timeout reached.';
        default:
            return null;
    }
}

function myClick(id) {
    google.maps.event.trigger(markers[id], 'click');
}

function initMap() {
    fetch("/stations").then(response => {
        return response.json();
    }).then(data => {

            console.log("data: ", data['station']);
            map = new google.maps.Map(document.getElementById("map"), {
                zoom: 15,
                center: myLatLng,
            });
            var searchBox = new google.maps.places.SearchBox(
                (document.getElementById('searchBox')));
            $("#searchBox").submit(function (e) {
                e.preventDefault();
            });

            // Listen for the event fired when the user selects an item from the
            // pick list. Retrieve the matching places for that item.
            google.maps.event.addListener(searchBox, 'places_changed', function () {
                var places = searchBox.getPlaces();

                for (var i = 0, marker; marker = search_markers[i]; i++) {
                    marker.setMap(null);
                }

                // For each place, get the icon, place name, and location.
                search_markers = [];
                var bounds = new google.maps.LatLngBounds();
                var place = null;
                var viewport = null;
                for (var i = 0; place = places[i]; i++) {
                    var image = {
                        url: place.icon,
                        size: new google.maps.Size(71, 71),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(17, 34),
                        scaledSize: new google.maps.Size(25, 25)
                    };

                    // Create a marker for each place.
                    var marker = new google.maps.Marker({
                        map: map,
                        icon: image,
                        title: place.name,
                        position: place.geometry.location
                    });
                    viewport = place.geometry.viewport;
                    search_markers.push(marker);

                    bounds.extend(place.geometry.location);
                }
                map.setCenter(bounds.getCenter());
            });

            // Bias the SearchBox results towards places that are within the bounds of the
            // current map's viewport.
            google.maps.event.addListener(map, 'bounds_changed', function () {
                var bounds = map.getBounds();
                searchBox.setBounds(bounds);
            });

            const current_marker = new google.maps.Marker({position: {lat: 53.3531, lng: -6.2580}, icon:"http://maps.google.com/mapfiles/ms/icons/blue-dot.png", map});
            trackLocation({
                onSuccess: ({coords: {latitude: lat, longitude: lng}}) => {
                    current_marker.setPosition({lat, lng});
                    map.panTo({lat, lng});
                    // Print out the user's location.
                    $info.textContent = `Current Location Found! Lat: ${lat} Lng: ${lng}`;
                    // Don't forget to remove any error class name.
                    $info.classList.remove('error');
                    $info.classList.add('success');
                },
                onError: err => {
                    // Print out the error message.
                    $info.textContent = `Error: ${getPositionErrorMessage(err.code) || err.message}`;
                    // Add error class name.
                    $info.classList.add('error');
                    $info.classList.remove('success');
                }
            });
            var count = 0;
            data['station'].forEach(station => {
                console.log(station);
                console.log(station.weather_main);
                const infowindow = new google.maps.InfoWindow({
                    content: '<h1>' + station.address + '</h1>' + '<p>Available Bikes: ' + station.available_bikes + '</p>' + '<p>Available Bike Stands: ' + station.available_bike_stands + '</p><p>' + station.weather_main + '</p><p>' + station.last_update + '</p>',
                });

                const marker = new google.maps.Marker({
                    position: {lat: station.position_lat, lng: station.position_lng},
                    map,
                    title: "Hello World!",
                });

                google.maps.event.addListener(marker, 'click', function () {
                    activeInfoWindow && activeInfoWindow.close();
                    infowindow.open(map, marker);
                    activeInfoWindow = infowindow;
                });
                markers.push(marker);

                function infoCallback(content, marker) {
                    return function () {
                        infowindow.setContent(content);
                        infowindow.open(map, marker);
                    };
                }

                $("#bikes_list").append('<a href="#" onclick="myClick(' + count + ');" class="list-group-item list-group-item-action flex-column align-items-start"><div className="d-flex w-100 justify-content-between">\n' +
                    '                    <h5 class="mb-1">' + station.address + '</h5>\n' +
                    '                    <small>' + station.last_update +
                    '+</small>\n' +
                    '                </div>\n' +
                    '                <p class="mb-1">Available Bikes:' + station.available_bikes + '</p>\n' +
                    '                <small>' + station.weather_main + '</small>\n' +
                    '            </a>'
                )
                ;
                count++;
            });

        }
    )
    /*
        var searchBox = new google.maps.places.SearchBox(document.getElementById('searchBox'));
        const options = {
            componentRestrictions: {country: "ie"}
        };
        const autocomplete = new google.maps.places.Autocomplete(searchBox, options);
        autocomplete.bindTo("bounds", map);
    */

}



