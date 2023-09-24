You'll need to create an IAM role ahead of time with full permissions (or add specific permissions as needed) to deploy using the cdk/sam CLI

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv on linux, macOS, or windows mingw

```
$ source .env/Scripts/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
$ pip install wheel
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

 To bootstrap in a new region/account

 cdk --profile zzz bootstrap

 where zzz is a profile specified in ~/.aws/credentials

 To deploy

 cdk --profile zzz deploy CdkStack

## Permission setup
IAM Identity center is set up for sso.  Once you have an account enabled, run

```
aws configure sso
```

```
SSO start URL [None]: https://d-9267521077.awsapps.com/start
SSO Region [None]: us-west-2
...
CLI default client Region [None]: us-west-2
CLI default output format [None]: json
CLI profile name [...]: dev2
```

Now your aws cli has a `dev2` profile that can be used for access.  Daily access is achieved by running
```
aws sso login --profile dev2
```

CDK 1 doesn't support it yet so use `yawsso` to copy the credentials over to a `dev2` profile in `~/.aws/credentials`.

```
yawsso
```

## Other useful commands

 * `cdk ls --profile dev2`          list all stacks in the app
 * `cdk synth --profile dev2`       emits the synthesized CloudFormation template
 * `cdk deploy --profile dev2`      deploy this stack to your default AWS account/region
 * `cdk diff --profile dev2`        compare deployed stack with current state
 * `cdk docs`                       open CDK documentation

## Rust build

One time setup
* Install [cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html)
* Install cargo-lambda in python venv `pip3 install cargo-lambda`
* Install zig in python env `pip3 install ziglang`

Every new terminal 😒
* Zig doesn't set up the path correctly, so run
    * `source .zigpath`

Building
* cd to the function dir
    * `cd PollyFunction`
* build
    * `cargo lambda build --release`
* or debug
    * `cargo lambda watch`
    * `cargo lambda invoke PollyFunction --data-ascii '{}'`

## Rust vs Python lambda
I measured the runtime of lambda executions using the rust and python variants of this function.  Some executions were cold starts.

### Python
---
| p01 | p25 | p50 | p90 | p99 | count |
| --- | --- | --- | --- | --- | --- |
| 95.8437 | 238.7132 | 264.0695 | 413.2235 | 594.5511 | 221 |
---
### Rust
---
| p01 | p25 | p50 | p90 | p99 | count |
| --- | --- | --- | --- | --- | --- |
| 52.406 | 91.4454 | 113.708 | 279.8303 | 351.8022 | 158 |
---

## Troubleshooting
### (Windows) failed to run custom build command for `ring v0.16.20` ... error occurred: Failed to find tool. Is `ar` installed?
If the rust build cannot find `ar`, you have to get it and copy the executable over to `~/.rustup/toolchains/stable-x86_64-pc-windows-gnu/bin/` for example.  One way to get `ar.exe` is from the msys2 mingw-w64-x86_64-binutils package.
