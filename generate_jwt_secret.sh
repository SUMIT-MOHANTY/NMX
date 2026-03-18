
# Generate a secure random key
JWT_SECRET=$(openssl rand -hex 32)

# Display the key
echo "Generated JWT_SECRET_KEY: ${JWT_SECRET}"
echo "Add this to your .env file:"
echo "JWT_SECRET_KEY=${JWT_SECRET}"

# Check if .env file exists
if [ -f .env ]; then
  # Check if JWT_SECRET_KEY already exists in .env
  if grep -q "JWT_SECRET_KEY=" .env; then
    echo "JWT_SECRET_KEY already exists in .env file."
    echo "Replace it manually if you want to update it."
  else
    # Append to .env file
    echo "JWT_SECRET_KEY=${JWT_SECRET}" >> .env
    echo "JWT_SECRET_KEY added to .env file."
  fi
else
  # Create .env file
  cp .env.example .env
  sed -i "s|JWT_SECRET_KEY=your-secure-secret-key-here|JWT_SECRET_KEY=${JWT_SECRET}|" .env
  echo ".env file created with JWT_SECRET_KEY."
fi
