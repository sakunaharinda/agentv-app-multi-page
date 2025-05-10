#!/bin/bash

export $(grep -v '^#' .env | xargs)

# Prompt for user inputs
read -p "Username: " username
read -p "Email: " email
read -p "First name: " firstname
read -p "Last name: " lastname
read -s -p "Password: " password
echo

hashed_password=$(python3 pass_gen.py "$password" 2>/dev/null | tail -n 1)

mongo_cmd=$(cat <<EOF
db.getSiblingDB("agentv").user.insertOne({
  user: {
    "$username": {
      email: "$email",
      first_name: "$firstname",
      last_name: "$lastname",
      password: "$hashed_password",
      roles: ["user"]
    }
  }
})
EOF
)

# docker exec -i agentv-app-db mongosh agentv --quiet --eval "$mongo_cmd"
mongosh "$MONGODB_URI" --eval "$mongo_cmd"

echo "User '$username' added to MongoDB."
