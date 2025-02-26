import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useSelector } from "react-redux";

const fetchFeedbacks = async () => {
  const { data } = await axios.get("http://127.0.0.1:8000/api/feedbacks/");
  return data;
};

const Dashboard = () => {
  const { data, isLoading, error } = useQuery({ queryKey: ["feedbacks"], queryFn: fetchFeedbacks });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error loading feedbacks</p>;

  return (
    <div className="p-5">
      <h1 className="text-2xl font-bold">Feedback Dashboard</h1>
      <table className="mt-5 w-full border-collapse border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">Title</th>
            <th className="border p-2">Upvotes</th>
            <th className="border p-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {data.map((feedback) => (
            <tr key={feedback.id}>
              <td className="border p-2">{feedback.title}</td>
              <td className="border p-2">{feedback.upvotes}</td>
              <td className="border p-2">{feedback.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
