# Marsten: Markov Stenography

A silly little toy that lets you hide messages in the output of a Markov chain model.

Usage:

```
# Grab some source document to train your model
curl -O http://www.gutenberg.org/cache/epub/10/pg10.txt

# Create a markov model
python create_model.py bible.model pg10.txt

# Encode your message
echo "This is a test" | python encode.py bible.model > encoded.txt

# Decode your message
< encoded.txt python decode.py bible.model
```
