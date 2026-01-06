# Chat

## Features

- Multi channel
- Multi user
- Persistent message history
- Authenticated and Guest Users
- User Presence
- Typing indicator
- Reactions

## TODOs

- [ ] Add **Redis** for *scaling* and improve *performance*
- [ ] Improve **Reactions**
  - [ ] Keep track of who reacted
  - [ ] Persistent reactions
- [ ] Make **message protocol payload** smaller for *efficiency*
  - [ ] Use *bit fields* instead of `StrEnum` for the `MessageType`
  - [ ] Smaller fields, e.g. `user` -> `u`
- [ ] Add **pagination** for the message history
- [ ] Add typing indicator
- [ ] Add **slash commands**
  - [ ] Kick user
  - [ ] Mute user
- [ ] Add **more tests**

## Message Protocol

The communication is done entirely in WebSockets.

### Creating new protocols

I focused in making easy and modular when implementing new protocols.

First create a `MessageType` enum that will be used to identify this protocol.

Create a `handler` for your protocol inside `server/handler/` that will contain
your **implementation** of the protocol.

And **register** this `handler` to a `MessageType` inside `server/handler/routes.py`

After this the server will send every request of this new `MessageType`
to the specified `handler`.
