{ lib
, runCommand
, wordswurst
, sassc
}:

{
  basic = runCommand "wordswurst-ci" { } ''
    ${sassc}/bin/sassc ${wordswurst.src}/tests/article.scss article.css
    cp ${wordswurst.src}/tests/{article,content}.wwst ./
    ${wordswurst}/bin/wordswurst article.wwst > $out
  '';
}
