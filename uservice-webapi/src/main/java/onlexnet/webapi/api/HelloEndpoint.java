package onlexnet.webapi.api;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** Redirects to graphiql console to make development easier */
@RestController
class HelloEndpoint {
    
    @GetMapping("/")
    public ResponseEntity<?> root() {
        var headers = new HttpHeaders();
        headers.add("Location", "/graphiql");    
        return new ResponseEntity<String>(headers, HttpStatus.FOUND);  
  }
    
}
