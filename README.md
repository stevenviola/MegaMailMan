# MegaMailMan


MegaMailMan is a service which can send e-mail through several different e-mail providers, such as SendGrid, MailGun, and Mandrill. MegaMailMan is able to switch between providers depending on availability of the service or based on user preference. MegaMailMan provides a RESTful API for specifying different fields of an e-mail, which are translated to the specifications of the service being used to send the e-mail.

MegaMailMan is mainly a backend application deployed on Google App Engine, but does have a simple frontend to interact with the functionality of the API. The application is currently deployed on Google App Engine and can be accessed here: https://mega-mailman.appspot.com/. The API can be interactivly tested using this frontend, or [Google's API Explorer](http://apis-explorer.appspot.com/apis-explorer/?base=https://mega-mailman.appspot.com/_ah/api#p/megamailman/v1/megamailman.mail.send). Details about the technologies used for this application are [documented further down in this README](https://github.com/stevenviola/MegaMailMan#technologies-used)

![Standards](http://imgs.xkcd.com/comics/standards.png)

# Configuration

In order to configure the services, you will need to create a file called config.yaml. In this file, you will need to put the API keys or the username/passwords in order to authenticate to the services. The config file should look like the following:

    sendgrid:
        url: https://api.sendgrid.com/api
        user: <username>
        password: <password>

    mailgun:
        url: https://api.mailgun.net/v2
        domain: <subdomain>.mailgun.org
        user: api
        password: <key from website here>
    
    mandrill:
        url: https://mandrillapp.com/api/1.0
        key: <key from website here>

# Installation

MegaMailMan is designed to be deployed on Google App Engine. In order to deploy to Google App Engine, follow these easy steps:

1) Go to the [Google Developers Console](https://console.developers.google.com/project) and click on Create Project

2) Fill out the form, and take note of your Project ID

3) clone this repo and save to the name of the project ID
> git clone https://github.com/stevenviola/MegaMailMan.git <project id>

4) Copy the config template.yaml and fill out with credentials from the services
> cp config.template.yml config.yaml

5) Update app.yaml and set the application to be the project id

6) Deploy to Google App Engine
> google_appengine/appcfg.py update [project id]/

7) Go to the webapp [project id].appspot.com

## Webapp


The frontend is a webapp that demonstrates the features of the MegaMailMan API. Through this app, you can fill out the fields of the e-mail, and select from the available services which services you want to try to send an e-mail with. If no services are selected, than by default, the API will try to send an e-mail via all available services, sequentially as they are listed in this app, until the e-mail is sent successfully. When you submit the e-mail information, a message will appear letting you know your e-mail was sent and what service it was sent with. If there is an error with a field, you will get a warning. In the event that none of the selected services are available for use, an error message will appear informing you the e-mail could not be sent.


## API

The API takes a JSON object in the POST Data with all the information about the e-mail to be sent. An example of the JSON to be sent looks like this

    {
      "sender": "steve@example.com",
      "to": [
        "alice@exam",
        "bob@example.com"
      ],
      "cc": [
        "cody@example.com",
        "dave@example.com"
      ],
      "bcc": [
        "eric@example.com",
        "frank@example.com"
      ],
      "subject": "This is the subject of the e-mail",
      "body": "This is the body of the e-mail. ",
      "services": [
        "sendgrid",
        "mailgun",
        "mandrill"
      ]
    }

Below is a description of each of the fields

#### Sender

String - Required -  This must be an e-mail address which will be set as the sender of the e-mail. There can only be one sender of an e-mail.

If there is no sender set, the API will return with the following error message:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field sender)",
        "reason": "badRequest"
       }
      ],
      "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field sender)"
     }
    }

If the sender is not a valid e-mail address, the API will return with the following error message:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "The address stevenviola in the sender field is invalid",
        "reason": "badRequest"
       }
      ],
      "message": "The address stevenviola in the sender field is invalid"
     }
    }

#### To

Array - Required - This array must have at least one e-mail address in it, as an e-mail needs to be sent to someone. There can be any number of additional e-mail addresses in the array, but they need to be using the valid e-mail address format

If there is no to field set, the API will return the following error message:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "Nothing set for the to field",
        "reason": "badRequest"
       }
      ],
      "message": "Nothing set for the to field"
     }
    }

If there is a invalid formatted e-mail address in the to field, then the API will return with the following error:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "The address to in the to field is invalid",
        "reason": "badRequest"
       }
      ],
      "message": "The address to in the to field is invalid"
     }
    }

#### CC

Array - Optional - This array is optional and will set the cc fields of the e-mail to be sent. All e-mails in this list need to be properly formatted.

If there is a invalid formatted e-mail address in the cc field, then the API will return with the following error: 

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "The address stevenviola in the cc field is invalid",
        "reason": "badRequest"
       }
      ],
      "message": "The address stevenviola in the cc field is invalid"
     }
    }

#### BCC

Array - Optional - This array is optional and will set the bcc fields of the e-mail to be sent. All e-mails in this list need to be properly formatted.

If there is a invalid formatted e-mail address in the bcc field, then the API will return with the following error: 

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "The address stevenviola+bcc in the bcc field is invalid",
        "reason": "badRequest"
       }
      ],
      "message": "The address stevenviola+bcc in the bcc field is invalid"
     }
    }

#### Subject

String - Required - This string is set as the e-mail Subject. It is required in order to send an e-mail.

If there is no subject field set, the API will return the following error message:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field subject)",
        "reason": "badRequest"
       }
      ],
      "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field subject)"
     }
    }

#### Body

String - Required - This string is set as the e-mail body. It is required in order to send an e-mail.

If there is no body field set, the API will return the following error message:

    {
     "error": {
      "code": 400,
      "errors": [
       {
        "domain": "global",
        "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field body)",
        "reason": "badRequest"
       }
      ],
      "message": "Error parsing ProtoRPC request (Unable to parse request content: Message CombinedContainer is missing required field body)"
     }
    }

#### Services

Array - Optional - This array specifies the services to try and use to send the e-mail. If this array is not present in the request or if it is empty, then by default, all services will be tried. Services that are invalid will be skipped

The valid services are:

* sendgrid
* mailgun
* mandrill

If the API can not send an e-mail with any of the services, it will respond with the following error:

    {
       "error": {
       "code": 503, 
       "errors": [
        {
         "domain": "global", 
         "message": "Exhausted services to send email with", 
         "reason": "backendError"
        }
       ], 
       "message": "Exhausted services to send email with"
      }
    }

###API Explorer


This API is built using Google Cloud Endpoints, which provides an API Explorer User interface to interactively test the API without the need of a client application. You can access [the API Explorer for MegaMailMan here](http://apis-explorer.appspot.com/apis-explorer/?base=https://mega-mailman.appspot.com/_ah/api#p/megamailman/v1/megamailman.mail.send). The API Explorer will provide useful information for testing different scenarios, including response headers, the raw JSON Response, and the Fields used to POST the information to the API

## Tests

In the tests directory, there is a file called api_tests.sh which has several use cases for testing the API and verifying the response codes. This is to ensure the API is functional and responding according to the above API documentation. The tests select each service and ensures that they all react the same way to the same inputs.

To run the tests, make sure the API variable in the script is correct for the current deployment. Run the following command to invoke the checks:

    ./api_tests.sh

There will be lots of verbose messages that are on STDOUT. If an error happens, then it is output on STDERR. To ignore the verbose messages, redirect STDOUT to /dev/null, like so

    ./api_tests.sh 1>/dev/null

Once the script completes its run, you can check the exit code to make sure it passed the tests. An exit code of 0 means the tests have passed

    $ echo $?
    0

If there is an issue, then the script will exit with a code of 2.

This script could be loaded into a continuous integration tool, such as Jenkins to ensure the API is performing as it should be as development is being done.

# Technologies Used

## Backend

The backend is written in Python and from the start was designed to run on [Google App Engine](https://cloud.google.com/appengine/docs). This was chosen because of the simplicity of managing the service once deployed. Google App Engine is also serving up the front end webapp, so deployment is very simple. 

Each e-mail service was written as a module, and each service has a function called send_mail which accepts the same parameters. For each service, the module acts differently due to quirks in each of the services APIs. For example, sendgrid requires multiple cc recipients to be passed to the api like this:

    cc[]=cc1@example.com&cc[]cc2@example.com

This is completely different than other services, so the API for each service had to be researched, and expose itself as a blackbox so that the services could be used interchangeably without the API needing updates.

### Google Cloud Endpoints

The API uses [Google Cloud Endpoints](https://cloud.google.com/appengine/docs/python/endpoints/) to expose an API that can be used directly with cURL or also using the Google API Javascript Client. Google Cloud Endpoints includes features that would take more time to setup manually, including SSL support and OAuth. OAuth support was something I wanted to add, especially to counter the API being used for spam, but complicated the demo and testing. Google Cloud Endpoints also does some checking on the fields, to ensure that required fields are set.

Given additional time, enabling OAuth would be the first thing to do to make the API more robust

### NDB Datastore

Although only used slightly for this application, e-mails sent through the API are stored in the [NDB datastore](https://cloud.google.com/appengine/docs/python/ndb/). It was intended that with OAuth, a user could authenticate and retrieve e-mails they sent through the API, using a GET request. This didn't make it into the demo of the application, and right now, the API just stores the e-mails using NDB, but can not retrieve them.

## Frontend

Although this is mainly a backend focused application, the frontend is intended to demonstrate the functionality of the API. 

### Bootstrap

[Bootstrap](http://getbootstrap.com/) made it super simple to make the frontend responsive so that the UI looks good even on a screen size of 400px wide. I make heavy use of Bootstraps Input styling and buttons to make the simple interface look clean and modern.

### jQuery

The Interface has several options that repeat, such as the To, CC, and BCC, and by using [jQuery](http://jquery.com/), I can easily clone the DOM elements for these so the user can add and remove recipients when filling out the form. I am also using a [jQuery validation plugin](http://jqueryvalidation.org/) to validate the form fields that are required.

## TODO

There were some things that had to be left out from this project due to time constraints and for simplicity sake.

- OAuth Security on the API
    - The API needs security in order not to be a method for bad people to use for sending spam. The added benefit with adding OAuth is being able to keep track of the users e-mails for retrieval in the future.

- Get listing of sent e-mails
    - Coupled with the OAuth Security, this feature would allow the logged in user to get a list of e-mails only they sent. You would only get e-mails you sent, and not ones that other users have sent

- Handling webhook callbacks from services
    - Documented in the API for the services used, there are webhooks that the service can send if the e-mail was bounced back, or successfully delivered. Originally, this was planned to handle the async callbacks from the services in order to update the state of the email stored in the datastore

## Credit

All code was written by Steven Viola.

E-mail services provided by SendGrid, MailGun, and Mandrill.
