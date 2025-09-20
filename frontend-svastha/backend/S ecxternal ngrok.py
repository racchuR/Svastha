from pyngrok import ngrok

ngrok.set_auth_token("YOUR_NGROK_AUTHTOKEN")  # Replace with your actual token

ngrok_tunnel = ngrok.connect(5000, "http")
print(f"Public URL: {ngrok_tunnel.public_url}")