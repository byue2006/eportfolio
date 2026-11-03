/*
  Personal page categories, in the order they appear.

  Each category matches a folder in personal/ with the same name:
  personal/volleyball/, personal/basketball/, personal/music/, personal/photography/.
  Photos uploaded to a folder show up in that category automatically.

  You can edit the text here on GitHub (pencil icon, then "Commit changes"):
    title  - the heading
    blurb  - one or two sentences under the heading (leave "" to show nothing)
    link   - optional button, e.g. to a related page on the site
    cover  - optional: file name of the photo to use on the category tile
             (otherwise the first photo in the folder is used)
*/
window.PERSONAL_CATEGORIES = [
  {
    key: "volleyball",
    title: "Volleyball",
    blurb: "I play, and I've coached it: first as an assistant for the middle school boys' and girls' teams at Tsinghua International School in Beijing, then as head coach of the girls' team in my senior year.",
    link: { href: "leadership/coaching.html", text: "Coaching" }
  },
  {
    key: "basketball",
    title: "Basketball",
    blurb: "I play, and I coached the middle school girls' team at Tsinghua International School, first as an assistant and then as head coach in my senior year.",
    link: { href: "leadership/coaching.html", text: "Coaching" }
  },
  {
    key: "music",
    title: "Music",
    blurb: "I play trombone in the Duke University Marching Band. In high school I played in concert, pop, and jazz ensembles."
  },
  {
    key: "photography",
    title: "Photography",
    blurb: "Architecture and light, mostly shot on a Canon DSLR. This first set is from the Forbidden City in Beijing."
  }
];
