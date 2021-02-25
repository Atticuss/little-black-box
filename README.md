## My Little Black Box

### Dgraph

#### Authorization

Dgraph does not ship with any kind of real auth system out of the box. The Enterprise version has some options for this, but we can implement our own authz check at the reverse proxy layer via Traefik.

The simplest solution could be implemented via an `IngressRoute` rule, e.g.:

```
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: dgraph-ingress
  labels:
    app: dgraph
spec:
  entryPoints:
    - dgraph
  routes:
  - match: Host(`dev.dgraph.dc1.veraciousdata.io`) && Headers(`Authorization`, `foobar`)
    kind: Rule
    services:
    - name: dgraph
      port: 9080
```

This would allow for our service to be protected via a secret provided via the `Authorization` header. However, due to how this value is specified, it becomes very difficult to inject a dynamic secret value into this point. Instead, we use Traefik's ForwardAuth capabilities with a dead-simple Golang app. The container source code can be found [here](/images/dgraph-auth) and the k8s deployment information can be found [here](/dgraph/dgraph-auth).

![Source: Traefik Documentation](/media/traefik-forwardauth.png)

Using ForwardAuth, we instruct Traefik to first forward all requests to our authz Golang app. This app does nothing more than check the value of the `Authorization` header against the shared secret provided via an environment variable. By using this pattern, we can utilize the Vault secret injector pattern, allowing us to house our shared secret within Vault.

Auth container definition with dynamic secret injection:

https://github.com/Atticuss/little-black-box/blob/1ef76969d1351ce3ed5e6d895e6f5744ffb59160/dgraph/standard/dgraph.yaml#L28-L37

Defining the Middleware, instructing Traefik to first route all requests to the auth container:

https://github.com/Atticuss/little-black-box/blob/1ef76969d1351ce3ed5e6d895e6f5744ffb59160/dgraph/standard/dgraph.yaml#L138-L146

The `IngressRoute` rule configured to utilize the middleware:

https://github.com/Atticuss/little-black-box/blob/1ef76969d1351ce3ed5e6d895e6f5744ffb59160/dgraph/standard/dgraph.yaml#L120-L136
