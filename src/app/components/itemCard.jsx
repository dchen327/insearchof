export const ItemCard = ({ item }) => {
  return (
    <div className="card is-shadowless">
      <div className="card-content px-4 py-">
        <div className="media mb-2 flex items-center">
          <div className="media-content">
            <p className="title is-4 mb-2">{item.title}</p>
            <div className="flex flex-row mb-0">
              <p className="is-6">{item.sellerUserID}</p>
              <p className="is-6 font-thin">•</p>
              <p className="is-6">3h</p>
            </div>
          </div>
          <div className="bg-gray-100 rounded">
            <p className="p-1 text-lg text-black is-4">${item.price}</p>
          </div>
        </div>
        <div className="content">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus nec
          iaculis mauris.
        </div>
      </div>
    </div>
  );
};
