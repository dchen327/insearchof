export const ItemCard = ({ item }) => {
  // only display first 200 chars of description
  const description =
    item.description.length > 200
      ? item.description.substring(0, 200) + "..."
      : item.description;

  const price = Number.isInteger(item.price)
    ? item.price
    : parseFloat(item.price).toFixed(2);

  return (
    <div className="card is-shadowless">
      <div className="card-content px-4 py-">
        <div className="media mb-2 flex items-center">
          <div className="media-content">
            <p className="title is-4 mb-2">{item.title}</p>
            <div className="flex flex-row mb-0">
              <p className="is-6">{item.user_name}</p>
              <p className="is-6 font-thin">•</p>
              <p className="is-6">{item.time_since_listing}</p>
            </div>
          </div>
          <div className="bg-gray-100 rounded">
            <p className="p-1 text-lg text-black is-4">${price}</p>
          </div>
        </div>
        <div className="content">{description}</div>
      </div>
    </div>
  );
};
