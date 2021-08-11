
# Mystery-Box 📦

Construct a developer environment in one command.

## Usage:

```bash
box up [--config <str>]
box launch
[--memory <memory>] [--disk <disk>] [--backend <backend>] [--playbook <str>]
box in [--user <user>]
box stop
```

## Description:

`box up` reads configuration from `box.yaml` in the current directory; `box launch` receives similar arguments from cli (since a file-based interface is not always ideal)

```yaml
user: user
ssh_public_path: /home/user/.ssh/id_rsa.pub
memory: 3G
disk: 30G
playbook: '/home/user/bootstrap.yaml'

```

## License

The MIT License

Copyright (c) 2021 Róisín Grannell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

