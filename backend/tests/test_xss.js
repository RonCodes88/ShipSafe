function renderComment(req, res) {
  const comment = req.query.comment;
  res.send("<div>" + comment + "</div>");
}
