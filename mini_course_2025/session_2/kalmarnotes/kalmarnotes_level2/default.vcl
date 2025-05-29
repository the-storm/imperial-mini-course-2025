vcl 4.0;

backend default {
    .host = "127.0.0.1";
    .port = "3000";
}

sub vcl_hash {
    hash_data(req.url);
    if (req.url ~ "\.(js|css|png|gif)$") {  
        return (lookup);
    }
}

sub vcl_recv {
    if (req.url ~ "\.(js|css|png|gif)$") {
        set req.http.Cache-Control = "max-age=10";
        return (hash);
    }
}

sub vcl_backend_response {
    if (bereq.url ~ "\.(js|css|png|gif)$") {
        unset beresp.http.Vary;
        set beresp.ttl = 10s;
        set beresp.http.Cache-Control = "max-age=10";
        unset beresp.http.Pragma;
        unset beresp.http.Expires;
    }
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }
    set resp.http.X-Cache-Hits = obj.hits;
}