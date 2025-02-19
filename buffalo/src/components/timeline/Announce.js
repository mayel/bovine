import { Link, Paper } from "@mui/material";
import React from "react";
import Actor from "./Actor";
import Source from "./Source";

const Announce = ({ entry }) => {
  const { actor, object } = entry;

  return (
    <Paper
      sx={{ backgroundColor: "white", padding: 2, margin: 2 }}
      elevation={2}
    >
      <Actor name={actor} /> announced{" "}
      <Link href={object} target="_blank">
        {object}
      </Link>
      <Source entry={entry} />
    </Paper>
  );
};

export default Announce;
