# Hackweek Website Template
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

**THIS IS A [TEMPLATE REPOSITORY](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template )** designed to streamline creating two linked websites for a [UW eScience Hackweek](https://uwhackweek.github.io/hackweeks-as-a-service/intro.html):

1. An event landing page built on a [Tech Conference Theme](https://themes.3rdwavemedia.com/demo/bs5/devconf/)
1. A [JupyterBook](https://jupyterbook.org/) for event content (including tutorials)

We've found that every hackweek benefits from a single-page website to get people's attention and consolidate important logistical details such as the 'who','what','why','when' of an event. In addition, JupyterBook provides a convenient means to consolidate and present tutorials with dynamic content such as executable code and dynamic figures.

## Examples

We've used this template for the following events:

* SnowEx Hackweek 2021: https://snowex-hackweek.github.io/website/intro.html


## How to use this template

You can use this template for your own event!

1. Click the "Use this template" button at the top of the repo
1. Select the account where you'd like to use the template.
1. **Be sure to select the checkbox to include all branches!** Otherwise your book will not be rendered automatically. You can remove all branches except for `main` and `gh-pages` from your new repo.
1. In your new repo, go to Settings > Pages to find the link to your JupyterBook. We recommend adding this link to the home page.
1. There are a few files you'll need to edit to customize content for your event:
  * `cookiecutter.yaml`:  customize your landing page content
  * `book/_config.yml`:  customize your JupyterBook content
  * `README.md`:  a basic description of your project
  * `CITATION.cff`:  add a standard citation file with all the event organizers


## Design

We've designed this template so that you should only have to edit a few files with intuitive syntax. When changes are pushed to GitHub, [continuous integration](./.github/README.md) takes care of converting these files into HTML and publishing the website.


## How to contribute

We are always trying to improve upon this template for future events and welcome contributions. Have a look at our [code of conduct](./CODE_OF_CONDUCT.md) and [contributing guide](./CONTRIBUTING.md).


## Contributors ✨

Thanks for this template goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://scottyhq.github.io"><img src="https://avatars.githubusercontent.com/u/3924836?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Scott Henderson</b></sub></a><br /><a href="#eventOrganizing-scottyhq" title="Event Organizing">📋</a> <a href="https://github.com/uwhackweek/jupyterbook-template/commits?author=scottyhq" title="Code">💻</a> <a href="#ideas-scottyhq" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-scottyhq" title="Content">🖋</a></td>
    <td align="center"><a href="http://psc.apl.uw.edu/people/investigators/anthony-arendt/"><img src="https://avatars.githubusercontent.com/u/4993098?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Anthony Arendt</b></sub></a><br /><a href="#eventOrganizing-aaarendt" title="Event Organizing">📋</a> <a href="#ideas-aaarendt" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-aaarendt" title="Content">🖋</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/landungsetiawan/"><img src="https://avatars.githubusercontent.com/u/17802172?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Landung "Don" Setiawan</b></sub></a><br /><a href="#eventOrganizing-lsetiawan" title="Event Organizing">📋</a> <a href="#ideas-lsetiawan" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-lsetiawan" title="Content">🖋</a> <a href="https://github.com/uwhackweek/jupyterbook-template/commits?author=lsetiawan" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/JessicaS11"><img src="https://avatars.githubusercontent.com/u/11756442?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jessica</b></sub></a><br /><a href="https://github.com/uwhackweek/jupyterbook-template/commits?author=JessicaS11" title="Code">💻</a> <a href="#ideas-JessicaS11" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-JessicaS11" title="Content">🖋</a></td>
    <td align="center"><a href="https://github.com/jomey"><img src="https://avatars.githubusercontent.com/u/178649?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Joachim Meyer</b></sub></a><br /><a href="https://github.com/uwhackweek/jupyterbook-template/commits?author=jomey" title="Code">💻</a> <a href="#ideas-jomey" title="Ideas, Planning, & Feedback">🤔</a> <a href="#content-jomey" title="Content">🖋</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
