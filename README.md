# wordswurst
I haven't really decided what wordswurst is, so for now I'll just call it an experimental platypus for single-sourcing documentation.

# What problem does this solve?
Clumsy whitespace control in existing ~templating ecosystems.

I want to single-source documentation for multiple distinct purposes across a cluster of related projects--while also supporting multiple output formats (specifically: mdoc, markdown, and generated Python code).

YAML and Jinja (via j2cli) are a fairly obvious approach, but their whitespace controls are too clunky to handle complex cases (even with a little masochism).

# How does it solve it?
wordswurst tilts the whitespace problem on its head by using a (currently unnamed) variant of CSS for controlling the plaintext layout.

# Tell me more...

This is an early working draft. I'm putting it up to consume and as a reference, but I'm not quite ready to do things like cut a version, suggest anyone else use it, or etc.

You'll have to read code for now. There's source here, and a working example in the resholve repo. The README at https://github.com/abathur/resholve/tree/master/docs has a little more detail.
