# wordswurst
I haven't really decided what wordswurst is, so for now I'll just call it an experimental platypus ~designed for single-sourcing documentation...

## What is this?

Since I don't really know how to categorize it, I'll give you a low-level list of its parts, and some higher-level comparisons of what they add up to.

### low level
wordswurst combines 3 things:
1. An unnamed semantic ~authoring language. This language has roughly free-form semantics.
    - By free-form, I mean a few things...
        - it doesn't force a set of semantics on you as in HTML
        - it is cheap to add arbitrary semantics; you don't have to write gobs of code to add each
        - core language affordances take up very few identifiers (and will eventually be namespaced out of the way if needed)
    - It is (at least for now) built on top of D★Mark.

2. Using the same language as above, a ~declarative templating DSL with affordances such as using CSS selectors to include content from a document using the language from #1.
    - In the long term, this affordance will hopefully support selecting from more sources, such as HTML/XML/YAML/etc.

3. An unnamed/uncategorized CSS ~dialect which adds  properties and functions helpful for controlling plain-text layout (i.e., the positioning and spacing of elements in a plain-text file or stream).
    - It reinterprets a few properties + functions from ~normal CSS and adds some idiomatic to the task at hand.

### higher level
Just some comparisons that address the sum of the lower-level parts:
- It's a bit like a template engine
    - but mostly-declarative instead of mostly-imperative (i.e., it doesn't have conditionals or loops)
- It's a bit like a layout engine for plain text
- It's an experiment in whether CSS is a fruitful format for expressing plain-text layouts.
- It's an experiment in authoring with flexible DIY semantics
    - wordswurst is re-using an existing language for this; it isn't ~invented-here, but I feel like it's rare enough to be worth calling out
- It's an experiment in whether a 3rd layer of content/style separation is the ~missing component that makes Web-first templating systems lackluster when it comes to plaintext.

## What problem does this solve?
Narrowly, it's an attempt to solve whitespace-control issues that plague a more "obvious" approach to documentation single-sourcing: YAML and Jinja (via j2cli). These issues are most-evident when trying to simultaneously target a line-based language like mdoc and a whitespace-significant language such as markdown.

Broadly, it's an attempt to make documentation single-sourcing viable even with multiple target/output formats.

## Tell me more...

This is an early working draft. I'm putting it up to consume myself--and as a reference for what I'm up to. But I'm not quite ready to do things like cut a version, suggest anyone else use it, or etc.

Sharp edges:
- You'll have to read code for now. There's source here, an absolutely skeletal example in [tests/](tests/), and a working example in the resholve repo (https://github.com/abathur/resholve/tree/master/docs has a little more detail).
- I've only covered things that I encounter on the golden path to my own use-cases. If your needs align with mine, you might be fine. If not, we'll need to saw on it. (Which is fine--I'm not hostile to external users.)
