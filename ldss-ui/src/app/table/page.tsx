import Header from "../../../components/Header";
import React from 'react';
import Table from "../../../components/Table";

export default function TablePage() {
  return (
    <>
      <Header />
      <main className="container mx-auto p-16">
        <Table />
      </main>
    </>
  );
}