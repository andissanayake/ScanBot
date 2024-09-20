import { Breadcrumb } from "antd";
import DocumentDashboard from "../features/document/DocumentDashboard";

export const DocumentPage = () => {
  return (
    <>
      <Breadcrumb
        style={{ margin: "16px 0" }}
        items={[{ key: 1, title: "Document Dashboard", separator: "/" }]}
      ></Breadcrumb>
      <DocumentDashboard />
    </>
  );
};
