import { motion } from "framer-motion";

export function Card({ title, children, failed }) {
  return (
    <motion.section initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}>
      <div className="rounded-lg border-l-4 border-indigo-500 bg-white p-4">
        <h3>{title}</h3>
        {children}
      </div>
      {failed && (
        <div role="alert" className="border-l-4 border-red-500 bg-red-50 p-4">Payment failed</div>
      )}
    </motion.section>
  );
}
