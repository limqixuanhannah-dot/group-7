#!/usr/bin/env expect
set timeout -1
set token_file "/home/ubuntu/.openclaw/workspace/gcloud-token.json"

spawn /home/ubuntu/google-cloud-sdk/google-cloud-sdk/bin/gcloud auth login --no-launch-browser

expect "Go to the following link"
set output $expect_out(buffer)
# Extract URL - simplified
regexp {https://accounts\.google\.com[^[:space:]]+} $output auth_url

puts "\n\n================================================"
puts "👉 Hannah, please visit this URL in your browser:"
puts ""
puts "$auth_url"
puts ""
puts "After signing in, you'll get a verification code."
puts "================================================"
puts ""
send_user "Paste the verification code here and press Enter: "
expect_user -re "(.*)\n"
set code $expect_out(1,string)
send "$code\r"
expect eof
