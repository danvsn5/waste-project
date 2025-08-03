// PieChartExample.tsx
import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const data = [
  { name: "Concrete", value: 40 },
  { name: "Wood", value: 25 },
  { name: "Plastic", value: 20 },
  { name: "Metal", value: 15 },
];

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7f50"];

const PieChartExample = () => {
  return (
    <PieChart width={400} height={300}>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        labelLine={false}
        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
        outerRadius={100}
        fill="#8884d8"
        dataKey="value"
      >
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
};

export default PieChartExample;
