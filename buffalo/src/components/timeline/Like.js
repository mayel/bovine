import { Favorite } from "@mui/icons-material";
import { Icon, Link, Paper } from "@mui/material";
import React from "react";
import Actor from "./Actor";
import Source from "./Source";

const Like = ({ entry }) => {
  const { actor, object } = entry;

  let contentString = "";

  if (entry?.content) {
    contentString = " with " + entry.content;
  }

  return (
    <Paper
      sx={{ backgroundColor: "white", padding: 2, margin: 2 }}
      elevation={2}
    >
      <Icon>
        <Favorite />
      </Icon>
      <Actor name={actor} /> liked{" "}
      <Link href={object} target="_blank">
        this post
      </Link>
      {contentString}
      <Source entry={entry} />
    </Paper>
  );
};

export default Like;
