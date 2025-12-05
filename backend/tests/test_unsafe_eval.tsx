import React from "react";

export default function DangerousComponent({ code }) {
  const result = eval(code);
  return <div>Executed: {result}</div>;
}
