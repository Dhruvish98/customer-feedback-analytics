// frontend/src/components/MarketPositioning.jsx
const MarketPositioning = () => {
    return (
      <div className="positioning-matrix">
        <ScatterPlot
          xAxis="Price Point"
          yAxis="Customer Satisfaction"
          data={productPositioning}
          competitors={competitorData}
          quadrants={[
            { label: "Premium Leaders", color: "#10b981" },
            { label: "Value Champions", color: "#3b82f6" },
            { label: "Budget Options", color: "#f59e0b" },
            { label: "Overpriced", color: "#ef4444" }
          ]}
        />
      </div>
    );
  };