# Simple web service to test NodePort exposure from a devcontainer
resource "kubernetes_deployment" "example_web" {
  metadata {
    name = "example-web"
    labels = {
      app = "example-web"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "example-web"
      }
    }
    template {
      metadata {
        labels = {
          app = "example-web"
        }
      }
      spec {
        container {
          image = "nginx:alpine"
          name  = "nginx"
          
          port {
            container_port = 80
          }
          
          # Create a simple custom index.html
          volume_mount {
            name       = "config-volume"
            mount_path = "/usr/share/nginx/html"
          }
        }
        
        # ConfigMap volume for custom HTML
        volume {
          name = "config-volume"
          config_map {
            name = kubernetes_config_map.example_web_content.metadata[0].name
            items {
              key  = "index.html"
              path = "index.html"
            }
          }
        }
      }
    }
  }
}

# ConfigMap for custom web content
resource "kubernetes_config_map" "example_web_content" {
  metadata {
    name = "example-web-content"
  }

  data = {
    "index.html" = <<-EOF
      <!DOCTYPE html>
      <html>
      <head>
        <title>NodePort Test Service</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f0f0f0;
          }
          .container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
          }
          h1 {
            color: #4285f4;
          }
          .success {
            color: #34a853;
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>NodePort Test Service</h1>
          <p>If you can see this page, your <span class="success">NodePort (30999)</span> is correctly exposed from the devcontainer!</p>
          <p>Current time: <span id="current-time"></span></p>
        </div>
        <script>
          // Update the time every second
          function updateTime() {
            document.getElementById('current-time').textContent = new Date().toLocaleString();
          }
          updateTime();
          setInterval(updateTime, 1000);
        </script>
      </body>
      </html>
    EOF
  }
}

# NodePort Service for the web service
resource "kubernetes_service" "example_web" {
  metadata {
    name = "example-web"
  }

  spec {
    selector = {
      app = "example-web"
    }
    
    port {
      port        = 80
      target_port = 80
      node_port   = 30999
    }
    
    type = "NodePort"
  }
}

# Output the service URL
output "example_web_url" {
  value = "http://$(minikube ip):30999"
}
