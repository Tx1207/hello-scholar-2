# Stable Spec Identity

Use this reference only when a classification creates a new Spec identity.

## Stable Identity Test

1. **Allocate once.** Set the ID to the global maximum existing Spec number plus one. Count rejected and superseded IDs; preserve at least three digits.
2. **Keep the owner boundary.** Reuse an established Topic owner. When none exists, use the narrow repository capability boundary established by Architecture, callers, adjacent Spec exclusions, or a confirmed Topic. The interface kind belongs in the design name.
3. **Name the cross-approach invariant.** Build the design name from the confirmed public capability, its stable material identity modifiers, and its interface kind. A selected approach, execution mode, or implementation choice remains in `Alternatives and Tradeoffs` unless the user made it part of the public identity.
4. **Cross-check.** Compare the ID, Topic, and design name with established ownership, complete capability wording, and candidate exclusions. Ask one identity question only when multiple choices remain equally supported.
5. **Bind the path.** Use `hello-scholar/specs/<topic-id>/SPEC-<number>-<design-name>/spec.md`. When the user has already authorized design or implementation and the evidence is unambiguous, create that path without a separate path-approval round.

| Project evidence | Topic | Design name |
| --- | --- | --- |
| Public batch retrieval API; synchronous entry selected from several approaches | `batch-retrieval` | `public-batch-retrieval-api` |
| Signed stateless session tokens replace opaque stored tokens | `session-auth` | `signed-stateless-session-tokens` |

**Completion:** one full path is selected and every path token is supported by stable identity evidence.
