# wordswurst
I haven't really decided what wordswurst is, so for now I'll just call it an experimental platypus ~designed for single-sourcing documentation...

Since I don't really know how to describe it, I'll describe it every which way:
- It's a bit like a template engine
    - but mostly-declarative instead of mostly-imperative (i.e., it doesn't have conditionals or loops)
- It's a bit like a layout engine for plain text
- It's an experiment in whether CSS is a fruitful format for expressing plain-text layouts.
- It's an experiment in authoring with flexible DIY semantics
    - wordswurst is re-using an existing language for this; it isn't ~invented-here, but I feel like it's rare enough to be worth calling out
- It's an experiment in whether a 3rd layer of content/style separation is the ~missing component that makes Web-first templating systems lackluster when it comes to plaintext.
- It's an attempt to solve whitespace-control issues that plague a more "obvious" approach to documentation single-sourcing: YAML and Jinja (via j2cli). These issues are most-evident when trying to simultaneously target a line-based language like mdoc and a whitespace-significant language such as markdown.


# Tell me more...

This is an early working draft. I'm putting it up to consume myself--and as a reference for what I'm up to. But I'm not quite ready to do things like cut a version, suggest anyone else use it, or etc.

Sharp edges:
- You'll have to read code for now. There's source here, an absolutely skeletal example in tests/, and a working example in the resholve repo (https://github.com/abathur/resholve/tree/master/docs has a little more detail).
- I've only covered things that I encounter on the golden path to my own use-cases. If your needs align with mine, you might be fine. If not, we'll need to saw on it. (Which is fine--I'm not hostile to external users.)
