# Chat

## Features

- Multi channel
- Multi user
- Persistent message history
- Authenticated and Guest Users
- User Presence
- Typing indicator
- Reactions
- Chat Commands (/command)
  - Kick

## TODOs

- [ ] Add **Redis** for *scaling* and improve *performance*
- [ ] Improve **Reactions**
  - [ ] Keep track of who reacted
  - [ ] Persistent reactions
- [ ] Make **message protocol payload** smaller for *efficiency*
  - [ ] Use *bit fields* instead of `StrEnum` for the `MessageType`
  - [ ] Smaller fields, e.g. `user` -> `u`
- [ ] Add **pagination** for the message history
- [X] Add typing indicator
- [X] Add **slash commands**
  - [X] Kick user
  - [ ] Mute user
- [ ] Add **more tests**

## Need fixing

- [ ] ChannelMember when leaving and joining is not the best.
  - Only sent when leaving all channels.

## Message Protocol

The communication is done entirely in WebSockets.

### Creating new protocols

I focused in making easy and modular when implementing new protocols.

All you need is:

1. Create a `MessageType` enum in `server/protocol/enums.py`  that will be used
to identify this protocol.
2. Create the **Payload Body** in `server/protocol/messages.py` that will
contain all the data that is needed.
3. Create a `handler` for your protocol inside `server/handler/` that will contain
your **implementation** of the protocol.
4. And **register** this `handler` to a `MessageType` inside `server/handler/routes.py`

After this the server will send every request of this new `MessageType`
to the specified `handler`.
