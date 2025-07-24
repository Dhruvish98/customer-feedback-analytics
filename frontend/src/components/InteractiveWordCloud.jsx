// frontend/src/components/InteractiveWordCloud.jsx
const InteractiveWordCloud = ({ data, onWordClick }) => {
    return (
      <WordCloud
        data={data}
        onWordClick={(word) => {
          // Show all reviews containing this word
          onWordClick(word);
        }}
        colorScale={d3.scaleOrdinal()
          .domain(['positive', 'negative', 'neutral'])
          .range(['#10b981', '#ef4444', '#f59e0b'])}
      />
    );
  };